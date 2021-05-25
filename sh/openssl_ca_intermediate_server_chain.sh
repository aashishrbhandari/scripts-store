##### Sign Process
##### CA -> Intermediate CA -> Server

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


##############################
# Create Intermediate CA CSR
###############################
openssl req \
-subj "/C=IN/ST=Maharashtra/L=Mumbai City/O=Information Security Systems/OU=IT Services/CN=intermediateca-signed-by-rootca.com" \
-newkey rsa:4096 -nodes \
-sha256 \
-out test_intermediateca_csr.pem \
-keyout test_intermediateca_key.pem



##############################
# Create Intermediate CA CERT
###############################
mkdir -p demoCA/newcerts
touch demoCA/index.txt demoCA/index.txt.attr
echo 01 > demoCA/serial
openssl ca \
-batch \
-days 360 \
-in test_intermediateca_csr.pem \
-extensions v3_intermediateca_ext \
-extfile <(printf "[v3_intermediateca_ext]\n \
basicConstraints=CA:TRUE, pathlen:0 \n \
keyUsage=critical, cRLSign, digitalSignature, keyCertSign \n \
extendedKeyUsage=serverAuth, clientAuth \n \
") \
-cert test_ca_cert.pem \
-keyfile test_ca_key.pem \
-out test_intermediateca_cert.pem

### When You Rerun this Script it can Give Error For Same Cert Being Recreated
### Since for Testing their no requirement of files which are inside `demoCA`
### You can un-comment below Line

# rm -rfv demoCA



# Create a Server Sign Request
#####################
# Create Server CSR
#####################
openssl req \
-subj "/C=IN/ST=Maharashtra/L=Mumbai City/O=Information Security Systems/OU=IT Services/CN=rootca-intermediateca-signed-servercert.com" \
-newkey rsa:4096 -nodes \
-sha256 \
-out test_server_csr.pem \
-keyout test_server_key.pem


##################################################
# Sign using Server Cert using Intermediate CA
##################################################

openssl x509 \
-req \
-days 360 \
-in test_server_csr.pem \
-extensions v3_server_ext \
-extfile <(printf "[v3_server_ext]\n \
basicConstraints=CA:FALSE\n \
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment\n \
subjectAltName = DNS:rootca-intermediateca-signed-servercert.com, DNS:*.rootca-intermediateca-signed-servercert.com \n \
") \
-CA test_intermediateca_cert.pem \
-CAkey test_intermediateca_key.pem \
-CAcreateserial \
-out test_server_cert.pem \
-sha256

