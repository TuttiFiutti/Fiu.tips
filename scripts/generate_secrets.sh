mkdir ../secrets
openssl req -x509 -newkey rsa:4096 -nodes -keyout ../secrets/privkey.pem -out ../secrets/fullchain.pem -days 365 -subj '//CN=localhost'
