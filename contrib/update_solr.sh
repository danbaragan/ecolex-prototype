if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <collection_name>"
    exit 1
fi
echo "Updating collection:$1"
cd solr-4.10.3/example/
rm -rf "solr/$1/data/index/*" && rm -rf "solr/$1/data/tlog/*"
cp ~/ecolex-prototype/configs/schema.xml "solr/$1/conf/schema.xml"
cp ~/ecolex-prototype/configs/data-config.xml "solr/$1/conf/data-config.xml"
