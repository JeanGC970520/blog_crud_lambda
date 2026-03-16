# generate a clean set of requirements and install them into a temporary directory
rm -rf ./services/blog_crud/package-temp
mkdir -p ./services/blog_crud/package-temp

# remove any existing archive so we start fresh (zip -r updates rather than replaces)
rm -f ./services/blog_crud/function.zip
rm -f ./infra/lambda/function.zip

uv export \
    --format requirements.txt \
    --output-file ./services/blog_crud/requirements.temp.txt \
    --no-dev \
    --quiet \
    --no-hashes

# install dependencies using a Linux build container so compiled extensions
# (Pillow/_imaging) match the Lambda runtime environment
# the official public.ecr.aws/lambda/python:3.9 image has the same OS as
# Lambda and includes pip

# use a build image with bash entrypoint; override default entrypoint so we can run commands
# lambci/lambda:build-python3.12 is a community image that mirrors Lambda build envs

docker run --rm --platform linux/amd64 \
    -v "$PWD/services/blog_crud/package-temp":/var/task \
    -v "$PWD/services/blog_crud/requirements.temp.txt":/tmp/requirements.txt \
    --entrypoint /bin/bash \
    public.ecr.aws/lambda/python:3.12 \
    -c "set -eux; pip install --upgrade -q pip setuptools wheel; pip install -q -r /tmp/requirements.txt -t /var/task"

# copy our handler
cp $PWD/services/blog_crud/handler.py $PWD/services/blog_crud/package-temp/

# create zip archive
cd $PWD/services/blog_crud/package-temp && zip -q -r ../function.zip . && cd ..
