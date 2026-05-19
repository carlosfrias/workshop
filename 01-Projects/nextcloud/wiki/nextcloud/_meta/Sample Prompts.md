# NextCloud Project — Sample Prompts

Ready-to-use prompts for common tasks. Copy and paste these directly.

## Deployment

```
Deploy NextCloud on fnet2. Use Docker Compose with MariaDB, Redis, and Nginx reverse proxy. Apply with --check first.
```

```
Create an Ansible playbook to install NextCloud on fnet2 (192.168.0.142) with: NextCloud app, MariaDB 10.11, Redis 7, and Nginx reverse proxy. Store data in /srv/nextcloud/.
```

## Status & Health

```
Check NextCloud status on fnet2. Are all Docker containers running? Is the web UI accessible?
```

```
Run a health check on all lab nodes. Report NextCloud-specific status for fnet2.
```

## Configuration

```
Configure DNS for nextcloud.home pointing to 192.168.0.142 using dnsmasq on the lab network.
```

```
Set up NextCloud admin account with ansible-vault encrypted credentials.
```

## Backup

```
Create a backup playbook that syncs NextCloud data from fnet2 to fnet1:/srv/archive/nextcloud/.
```

## Research

```
What's the recommended NextCloud Docker Compose stack for a small lab? Compare with ReinerNippes and robertdebock Ansible roles.
```