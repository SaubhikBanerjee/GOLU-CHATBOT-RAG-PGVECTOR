-- https://github.com/pgvector/pgvector

set search_path='public'

--PostgreSQL Version.
SELECT version();

--Creating the base table.
BEGIN;
	DROP TABLE IF EXISTS chunk;
	CREATE TABLE IF NOT EXISTS chunk  (	sectionid VARCHAR(1000),
										fileid BIGINT,
										sectiontext TEXT,
									    filename VARCHAR(500)
									  );
END TRANSACTION;

BEGIN;
ALTER TABLE chunk ADD COLUMN table_section TEXT;
END TRANSACTION;

--How many rows?
select count(*) from chunk;
--Total of 594 rows.


-- Creating a tsvector column for full text search
-- Creating a GIN index also for faster search.
BEGIN;
	alter table chunk 
	add column chunk_fts_doc tsvector
	generated always as (
    	setweight(to_tsvector('simple', sectiontext), 'A') 
		||setweight(to_tsvector('english', sectiontext), 'B') 
	)
stored;
CREATE INDEX idx_chunk_fts_doc ON chunk USING GIN(chunk_fts_doc);
END TRANSACTION;

--Adding sectionid as Primary Key.
BEGIN;
ALTER TABLE chunk ADD PRIMARY KEY (sectionid);
END TRANSACTION;

-- Remember !! all-MiniLM-L6-v2: By default, 
-- input text longer than 256 word pieces is truncated. 
select t1.sectionid, count(words)
from chunk t1 inner join lateral 
(select t2.sectionid,regexp_split_to_table(sectiontext,'\s+') words
 from chunk t2
 where t1.sectionid = t2.sectionid) t3
 on t1.sectionid=t3.sectionid
 group by t1.sectionid having count(words) >256;

/*****
There are 65 sections which has >256 word, so
those will not be vectorise correctlly.
*****/

SELECT * from chunk where sectionid='008193b0b86a45728072cba1bb6c9fd7';

--Altering the table to add a column of datatype vector(384)
/***** From Huging Face Documentation ******
all-MiniLM-L6-v2
This is a sentence-transformers model: It maps sentences & paragraphs 
to a 384 dimensional dense vector space and can be used for 
tasks like clustering or semantic search.
--sentence-transformers/all-mpnet-base-v2: Alternative with 768 dimension.
*/
BEGIN;
ALTER TABLE chunk ADD COLUMN doc_embedding vector(384);
END TRANSACTION;

--HNSW index
CREATE INDEX ON chunk USING hnsw (doc_embedding vector_cosine_ops);

-- Full text search with all configuration
set session vars.question = 'What is ZCSA_CUTREF_CON';
SELECT current_setting('vars.question');

--Lets understand
SELECT phraseto_tsquery('simple',current_setting('vars.question'));
SELECT to_tsvector('simple',current_setting('vars.question'));

SELECT 'match' 
WHERE to_tsvector('simple',current_setting('vars.question'))
	 @@ phraseto_tsquery('simple',current_setting('vars.question'));
	 
SELECT 'match' 
WHERE setweight(to_tsvector('simple', current_setting('vars.question')), 'A') 
		||setweight(to_tsvector('english', current_setting('vars.question')), 'B')
	 @@ phraseto_tsquery('simple',current_setting('vars.question'));

SELECT * FROM chunk
WHERE to_tsvector('simple', replace(sectiontext,'_','/'))
	 @@ to_tsquery('simple',replace('ZCSA_CUTREF_CON','_','/'));
	 
select to_tsvector('english', replace('ZCSA_CUTREF_CON','_','/'));

SELECT setweight(to_tsvector('simple', current_setting('vars.question')), 'A') 
		||setweight(to_tsvector('english', current_setting('vars.question')), 'B'); 

SELECT * from chunk where sectionid='ddc8014d6996435a8f78c7f987802958';

-- Set uour question nd run FTS!!
--set session vars.question = 'Scheduling Agreement types';
--set session vars.question = 'What does ZCSA_CUTREF_CON do?';
set session vars.question = 'What is a reason for rejection fields?';
--phraseto_tsquery with simple configuration
select * from (
select sectionid,sectiontext,
ts_rank(chunk_fts_doc, 
		phraseto_tsquery('simple',current_setting('vars.question'))) rnk
from chunk 
where chunk_fts_doc
	@@ phraseto_tsquery('simple',current_setting('vars.question'))
	) x
order by  rnk desc limit 10;

--phraseto_tsquery with english configuration
select * from (
select sectionid,sectiontext,
ts_rank(chunk_fts_doc, 
		phraseto_tsquery('english',current_setting('vars.question'))) rnk
from chunk 
where chunk_fts_doc
	@@ phraseto_tsquery('english',current_setting('vars.question'))
	) x
order by  rnk desc limit 10;

--plainto_tsquery with simple configuration
select * from (
select sectionid,sectiontext,
ts_rank(chunk_fts_doc, 
		plainto_tsquery('simple',current_setting('vars.question'))) rnk
from chunk 
where chunk_fts_doc
	@@ plainto_tsquery('simple',current_setting('vars.question'))
	) x
order by  rnk desc limit 10;

--plainto_tsquery with english configuration
select * from (
select sectionid,sectiontext,
ts_rank(chunk_fts_doc, 
		plainto_tsquery('english',current_setting('vars.question'))) rnk
from chunk 
where chunk_fts_doc
	@@ plainto_tsquery('english',current_setting('vars.question'))
	) x
order by  rnk desc limit 10;

--websearch_to_tsquery with english configuration
select * from (
select sectionid,sectiontext,
ts_rank(chunk_fts_doc, 
		websearch_to_tsquery('english',current_setting('vars.question'))) rnk
from chunk 
where chunk_fts_doc
	@@ websearch_to_tsquery('english',current_setting('vars.question'))
	) x
order by  rnk desc limit 10;

--all-mpnet-base-v2: Alternative with 768 dimension.
--By default, input text longer than 384 word pieces is truncated.
select t1.sectionid, count(words)
from chunk t1 inner join lateral 
(select t2.sectionid,regexp_split_to_table(sectiontext,'\s+') words
 from chunk t2
 where t1.sectionid = t2.sectionid) t3
 on t1.sectionid=t3.sectionid
 group by t1.sectionid having count(words) >384;
 
 --There are nothing greater than 384!
 
/****
all-mpnet-base-v2 
This is a sentence-transformers model: 
It maps sentences & paragraphs to a 768 dimensional 
dense vector space and can be used for 
tasks like clustering or semantic search.
By default, input text longer than 384 word pieces is truncated.
****/
BEGIN;
ALTER TABLE chunk ADD COLUMN doc_embedding_mpnet vector(768);
END TRANSACTION;

--HNSW index
CREATE INDEX ON chunk USING hnsw (doc_embedding_mpnet vector_cosine_ops);
 
/******
Summerization model: bart-large-cnn, 
Asymmetric symantic search: msmacro-distilbert-base-v4
***************************
convert_to_tensor=true
Good Read: https://huggingface.co/sentence-transformers/msmarco-distilbert-base-v4
This is a sentence-transformers model: It maps sentences & paragraphs 
to a 768 dimensional dense vector space and can be used for tasks 
like clustering or semantic search.

For my use case "Asymmetric symantic search" I will go wit this option.
Good read: https://www.sbert.net/examples/applications/semantic-search/README.html

******/

--this model is working.
BEGIN;
ALTER TABLE chunk ADD COLUMN doc_embedding_msmacro vector(768);
END TRANSACTION;

--HNSW index
CREATE INDEX ON chunk USING hnsw (doc_embedding_msmacro vector_cosine_ops);

--Doing some research about tables. Questions asked from table is not comming properly.
set search_path=public;
select count(*) from chunk; --594 -->606
select count(*) from chunk where doc_embedding_msmacro is null; --0-->12
DELETE FROM chunk WHERE sectionid IN ('34c39ad9-b2f1-4359-ac50-127574a56f54'
									  ,'8bf02003-df01-49c8-9a2a-89c9f43921cc'
									  ,'ab5c8db9-c716-4c4a-9132-ee6283d646aa'
									  ,'b5cb24d9-c328-4550-9cb7-0b1e82856804'
									  ,'7ccbbca7-310a-47da-8a66-dcf6ff13997a'
									  ,'0ec2063c-a0a0-418d-8af5-7ded8b832c87'
									  ,'7450b4f0-5375-432a-bf61-ec582ff8c83f'
									  ,'d3563339-0558-4c2a-a8cf-59d8ee8c904e'
									  ,'63199eeb-c0b4-452a-8948-4bcee38b9b95'
									  ,'c4492bd5-34af-41da-a6ba-e308cdcb1fc5'
									  ,'eee29575-e8f9-448e-beb4-07bd25a510ec'
									  ,'b6700eda-0fdf-4c51-a3c5-d319071b6ba9'
									);

--Creating the new base table.
BEGIN;
	DROP TABLE IF EXISTS chunk_sb;
	CREATE TABLE IF NOT EXISTS chunk  (	sectionid VARCHAR(1000),
										fileid BIGINT,
										sectiontext TEXT,
									    filename VARCHAR(500),
										table_section TEXT
									  );
END TRANSACTION;

--this model is working.
BEGIN;
ALTER TABLE chunk_sb ADD COLUMN doc_embedding_msmacro vector(768);
END TRANSACTION;

--HNSW index
CREATE INDEX ON chunk_sb USING hnsw (doc_embedding_msmacro vector_cosine_ops);

