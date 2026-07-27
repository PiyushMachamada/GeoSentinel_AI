import os
import time
import zipfile
import requests

from dotenv import load_dotenv


class ImageryDownloader:
    """
    Downloads Sentinel products from the Copernicus Data Space Ecosystem.

    Responsibilities
    ----------------
    - Authenticate with CDSE
    - Resolve PRODUCT_ID -> UUID
    - Download SAFE ZIP product
    """

    def __init__(self):
        load_dotenv()

        self.username = os.getenv("CDSE_USERNAME")
        self.password = os.getenv("CDSE_PASSWORD")

        self.access_token = None

        self.base_auth_url = (
            "https://identity.dataspace.copernicus.eu"
        )

        self.base_catalog_url = (
            "https://catalogue.dataspace.copernicus.eu"
        )

        self.base_download_url = (
            "https://download.dataspace.copernicus.eu"
        )

        # Reuse a single HTTP session
        self.session = requests.Session()

    # --------------------------------------------------
    # Authentication
    # --------------------------------------------------

    def authenticate(self):
        """
        Authenticate with CDSE and retrieve an OAuth access token.
        """

        if not self.username or not self.password:
            raise ValueError(
                "CDSE_USERNAME or CDSE_PASSWORD not found in .env"
            )

        print("\nAuthenticating with Copernicus Data Space...")

        token_url = (
            "https://identity.dataspace.copernicus.eu/"
            "auth/realms/CDSE/protocol/openid-connect/token"
        )

        response = self.session.post(
            token_url,
            data={
                "grant_type": "password",
                "client_id": "cdse-public",
                "username": self.username,
                "password": self.password,
            },
            timeout=30,
        )

        response.raise_for_status()

        self.access_token = response.json()["access_token"]

        print("Authentication successful.")

        return self.access_token

    # --------------------------------------------------
    # Resolve PRODUCT_ID -> UUID
    # --------------------------------------------------

    def get_product_uuid(self, product_name: str):

        if self.access_token is None:
            self.authenticate()

        url = (
            f"{self.base_catalog_url}/odata/v1/Products"
            f"?$filter=Collection/Name eq 'SENTINEL-2' "
            f"and startswith(Name,'{product_name}')"
        )

        print("\nSearching CDSE catalogue...")
        print(f"Product Name : {product_name}")

        response = self.session.get(
            url,
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        products = data.get("value", [])

        if not products:
            raise RuntimeError(
                f"Sentinel product not found:\n{product_name}"
            )

        product = products[0]

        print("\nResolved Product")
        print("----------------------------")
        print(f"Name : {product['Name']}")
        print(f"UUID : {product['Id']}")

        return product["Id"]

    # --------------------------------------------------
    # Download SAFE ZIP
    # --------------------------------------------------

    def download_product(
        self,
        product_id: str,
        output_path: str,
    ):
        if os.path.exists(output_path):
            if os.path.getsize(output_path) > 0 and zipfile.is_zipfile(output_path):
                print("\nUsing cached Sentinel download")
                print("----------------------------")
                print(f"Product ID : {product_id}")
                print(f"Path       : {output_path}")
                return output_path
            print("\nCached file is invalid, re-downloading...")
            try:
                os.remove(output_path)
            except OSError as exc:
                raise RuntimeError(
                    f"Failed to remove invalid cached download: {output_path}"
                ) from exc

        if self.access_token is None:
            self.authenticate()

        product_uuid = self.get_product_uuid(product_id)

        download_url = (
            f"{self.base_download_url}/odata/v1/Products"
            f"({product_uuid})/$value"
        )

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True,
        )

        print("\nStarting Sentinel download")
        print("----------------------------")
        print(f"Product ID : {product_id}")
        print(f"UUID       : {product_uuid}")
        print(f"Output     : {output_path}")

        response = self.session.get(
            download_url,
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            stream=True,
            timeout=600,
        )

        response.raise_for_status()

        total_size = int(
            response.headers.get(
                "Content-Length",
                0,
            )
        )

        downloaded = 0
        start_time = time.time()

        with open(output_path, "wb") as file:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if not chunk:
                    continue

                file.write(chunk)

                downloaded += len(chunk)

                elapsed = max(
                    time.time() - start_time,
                    0.001,
                )

                speed = (
                    downloaded
                    / 1024
                    / 1024
                    / elapsed
                )

                if total_size:

                    percent = (
                        downloaded
                        / total_size
                        * 100
                    )

                    print(
                        f"\r{percent:6.2f}% | "
                        f"{downloaded/1024/1024:8.1f} MB / "
                        f"{total_size/1024/1024:8.1f} MB | "
                        f"{speed:6.2f} MB/s",
                        end="",
                        flush=True,
                    )

                else:

                    print(
                        f"\rDownloaded "
                        f"{downloaded/1024/1024:.1f} MB",
                        end="",
                        flush=True,
                    )

        print("\n\nDownload complete.")
        print(f"Saved to: {output_path}")

        return output_path