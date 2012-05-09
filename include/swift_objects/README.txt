## For the swift tests you will need three objects to upload for the test
## examples below are a 512K object, a 500M object, and 1G object
dd if=/dev/zero of=swift_small bs=512 count=1024
dd if=/dev/zero of=swift_medium bs=512 count=1024000
dd if=/dev/zero of=swift_large bs=1024 count=1024000

## for the kongrequester swift tests you will need a normal object
dd if=/dev/zero of=normal_object bs=1024 count=1024
## and 3 small files containing a single byte each
echo -n 'a' > 1
echo -n 'b' > 2
echo -n 'c' > 3
## the multipart file download test will check for the string 'abc' in the
## assembled file

