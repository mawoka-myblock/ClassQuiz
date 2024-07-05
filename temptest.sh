echo "Hello world"

if [ ! -d /tmp/storage ]; then
    echo "making storage"
    mkdir /tmp/storage
else
    echo "storage already exists"

# end of file
fi
