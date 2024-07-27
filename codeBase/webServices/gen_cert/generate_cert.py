import subprocess
import os

# Paths to CA key and certificate
CA_KEY = "ca.key"
CA_CERT = "ca.crt"


# Directory to store client certificates
CLIENT_CERT_DIR = "client_certs"


def generate_client_certificate(client_name):
    client_key = os.path.join(CLIENT_CERT_DIR, f"{client_name}.key")
    client_csr = os.path.join(CLIENT_CERT_DIR, f"{client_name}.csr")
    client_cert = os.path.join(CLIENT_CERT_DIR, f"{client_name}.crt")

    # Generate client private key
    subprocess.run(["openssl", "genpkey", "-algorithm", "RSA", "-out", client_key], check=True)

    # Generate certificate signing request (CSR)
    subprocess.run(["openssl", "req", "-new", "-key", client_key, "-out", client_csr, "-subj", f"/CN={client_name}"], check=True)

    # Generate client certificate signed by CA
    subprocess.run([
        "openssl", "x509", "-req", "-in", client_csr, "-CA", CA_CERT, "-CAkey", CA_KEY,
        "-CAcreateserial", "-out", client_cert, "-days", "365", "-sha256"
    ], check=True)

    # Read and return the generated certificate and key
    with open(client_cert, "r") as cert_file:
        client_cert_content = cert_file.read()
    with open(client_key, "r") as key_file:
        client_key_content = key_file.read()

    return client_cert_content, client_key_content


if __name__ == "__main__":
    # Ensure the directory for storing client certificates exists
    os.makedirs(CLIENT_CERT_DIR, exist_ok=True)

    # Generate client certificate for a given client name
    client_name = "client1"
    cert, key = generate_client_certificate(client_name)

    print("Generated Client Certificate:")
    print(cert)
    print("Generated Client Private Key:")
    print(key)
