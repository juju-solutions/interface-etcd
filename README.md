# Overview

This interface layer handles the communication with Etcd via the `etcd`
interface.

# Usage

## Requires

This interface layer will set the following states, as appropriate:

  * `{relation_name}.connected` The relation is established, but Etcd may not
  yet have provided any connection or service information.

  * `{relation_name}.available` Etcd has provided its connection string
    information, and is ready to serve as a KV store.
    The provided information can be accessed via the following methods:
      * `connection_string()`


For example, a common application for this is configuring an applications backend
kv storage, like Docker.

```python
@when('etcd.available', 'docker.available')
def swarm_etcd_cluster_setup(etcd):
    con_string = etcd.connection_string().replace('http', 'etcd')
    opts = {}
    opts['connection_string'] = con_string
    render('docker-compose.yml', 'files/swarm/docker-compose.yml', opts)

```


## Provides

A charm providing this interface is providing the Etcd rest api service.

This interface layer will set the following states, as appropriate:

  * `{relation_name}.connected` One or more clients of any type have
    been related.  The charm should call the following methods to provide the
    appropriate information to the clients:

    * `{relation_name}.provide_connection_string()`

Example:

```python

@when('db.connected')
def send_connection_details(client):
    etcd = EtcdHelper()
    data = etcd.cluster_data()
    hosts = []
    for unit in data:
        hosts.append(data[unit]['private_address'])
    client.provide_connection_string(hosts, config('port'))

```


# Contact Information

### Maintainer
- Charles Butler <charles.butler@canonical.com>


# Etcd

- [Etcd](https://coreos.com/etcd/) home page
- [Etcd bug trackers](https://github.com/coreos/etcd/issues)
- [Etcd Juju Charm](http://jujucharms.com/?text=etcd)
