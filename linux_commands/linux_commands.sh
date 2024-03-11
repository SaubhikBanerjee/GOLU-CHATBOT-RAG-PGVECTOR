sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo yum install -y postgresql14-server
sudo /usr/pgsql-14/bin/postgresql-14-setup initdb
sudo systemctl enable postgresql-14
sudo systemctl start postgresql-14
sudo yum install pgvector_14

sudo yum --disablerepo=* -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
cd /etc/yum.repos.d

sudo mv pgdg-redhat-all.repo pgdg-redhat-all.repoold
sudo mv pgdg-redhat-all.repo.rpmnew pgdg-redhat-all.repo.repo
sudo yum install pgvector_14
sudo yum install postgresql14-contrib

sudo yum install git

Error: Package: postgresql14-devel-14.11-1PGDG.rhel7.x86_64 (pgdg14)
           Requires: llvm-toolset-7-clang >= 4.0.1
Error: Package: postgresql14-devel-14.11-1PGDG.rhel7.x86_64 (pgdg14)
           Requires: llvm5.0-devel >= 5.0
Error: Package: postgresql14-devel-14.11-1PGDG.rhel7.x86_64 (pgdg14)
           Requires: perl(IPC::Run)

https://oracle-base.com/articles/linux/download-the-latest-oracle-linux-repo-file#oracle-linux-7-updated
/usr/pgsql-14/bin/pg_config
export PATH=$PATH:/usr/pgsql-14/bin
https://yum.oracle.com/repo/OracleLinux/OL7/developer/x86_64/index.html
sudo yum list all | grep -i postgre

ol7_developper.repo
[ol7_developer]
name=Oracle Linux $releasever Development Packages ($basearch)
baseurl=http://yum.oracle.com/repo/OracleLinux/OL7/developer/$basearch/
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-oracle
gpgcheck=1
enabled=1

 sudo yum install oracle-epel-release-el7.x86_64
 sudo yum --enablerepo=ol7_optional_latest install libedit-devel
 sudo yum install llvm5.0-devel
 sudo yum install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm

sudo rpm -ivh --nodeps postgresql14-devel-14.11-1PGDG.rhel7.x86_64.rpm
export PG_CONFIG=/usr/pgsql-14/bin/pg_config
sudo --preserve-env=PG_CONFIG make install




 