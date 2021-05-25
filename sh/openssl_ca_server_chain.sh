
#### Sign Process
#### CA -> Server

# Create a Root CA
##############
# Create CA
##############
openssl req \
-subj "/C=IN/ST=Maharashtra/L=Mumbai City/O=Information Security Systems/OU=IT Services/CN=Test Root CA" \
-x509 \
-newkey rsa:4096 -nodes \
-sha256 \
-out test_ca_cert.pem \
-keyout test_ca_key.pem \
-days 365


# Create a Server Sign Request
#####################
# Create Server CSR
#####################
openssl req \
-subj "/C=IN/ST=Maharashtra/L=Mumbai City/O=Information Security Systems/OU=IT Services/CN=direct-rootca-signed-cert.com" \
-newkey rsa:4096 -nodes \
-sha256 \
-out test_server_csr.pem \
-keyout test_server_key.pem


####################
# Sign using CA
####################
openssl x509 \
-req \
-days 360 \
-in test_server_csr.pem \
-extensions v3_server_ext \
-extfile <(printf "[v3_server_ext]\n \
basicConstraints=CA:FALSE\n \
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment\n \
subjectAltName = DNS:direct-rootca-signed-cert.com, DNS:*.direct-rootca-signed-cert.com \n \
") \
-CA test_ca_cert.pem \
-CAkey test_ca_key.pem \
-CAcreateserial \
-out test_server_cert.pem \
-sha256