# Animebyter

##### A daemon and web app that keeps track of the shows you watch and automatically downloads new episode off Animebytes.tv
----

### How to set-up
0) Set-up docker. This guide assumes that you use qBittorrent as a docker container and that you have some sort of web server with proxying capabilities, also dockerized.
1) Edit docker-compose:
   - Edit the `qbit-network` external name to the one that matches your qbittorrent network.
   - Edit the `qbit_url` enironment variable to the hostname of your qbittorrent server. This will typically be your container name (so make sure to set one).
   - Edit the `ab_key` environment variable with your animebytes passkey. You can find this under Settings > Account > Passkey.
   - Edit the `base_url` environment variable with the path that you've set on your reverse proxy. It should be `/` if you run it on a subdomain.
   - Edit the `gotify_url` to a valid Gotify server URL if you want to receive notifications.
2) Run `docker-compose up -d`. If you've set-up your docker-compose correctly it should run without problems.
3) Configure your reverse proxy. The docker-compose.yml provided, exposes a network called `animebyter-network` and names the container `animebyter`. You should edit the deployment of your web-server, making sure it is connected to the `animebyter-network`. The app should then be accessible on `animebyter:5000`. Here's a sample configuration for the caddy webserver:
```
proxy /animebyter animebyter:5000 {
    transparent
    without /animebyter
}
redir /animebyter /animebyter/

```

### How to use
The page shows two tables: Airing and Watching. You can add any show by clicking the (+) and remove it by clicking (-). Make sure to set a download path and preferably a label also. Also make sure to log into qBittorrent.

### Development

Want to contribute? Sure

License
----
MIT
