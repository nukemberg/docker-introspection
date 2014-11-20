# Docker introspection API

This is a small python HTTP server that allows to query information about Docker containers from within a container without exposing the entire Docker API.
The server only supports read-only access to one resource - container information. Currently there is no validation of request source.

## Usage

Install the server `pip install docker-instrospection`

Run the server `docker-instrospection`. Use `-h` to see command line options.

From within a container, get the container id then use `curl` to fetch information:

    CONTAINER_ID=$(cat /proc/self/cgroup |grep cpu:| sed -r 's#.*docker/(.{12}).*#\1#'­)
    # For v1.5 # CONTAINER_ID=$(cat /proc/self/cgroup | grep -w cpu | sed -r 's#.*docker-(.{12}).*#\1#')
    curl http://172.17.42.1:5000/containers/$CONTAINER_ID

Or better yet, just use the magic `_myself` container name to get your metadata:

    curl http://172.17.42.1:5000/containers/_myself
    
This is done by iterating on the metadata of all containers and comparing the source ip so it's probably not a good idea if you have a lot (> 1000) of containers and won't work if you are not using the internal network.

You probably want to define a bash function to do this easily:

```bash
function container_metadata () {
	CONTAINER_ID=$(cat /proc/self/cgroup |grep cpu:| sed -r 's#.*docker/(.{12}).*#\1#'­)
	if [[ -z "$1" ]]; then
    	curl http://172.17.42.1:5000/containers/$CONTAINER_ID
    else
    	curl http://172.17.42.1:5000/containers/$CONTAINER_ID/$1
    fi
}
```

The API will provide individual config items such as memory, volumes, etc. - just append the item name as the last url component.

The API output is currently json only. Use `jq` or whatever - i'll make this more friendly when I have some time.

The `--no-auth` flag will disable source IP checks thus allowing containers to view the metadata of all containers. It also disable the magic `_myself` container id.
