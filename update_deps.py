import subprocess
import requests
import sys

def get_latest_version(package_name):
    """Fetch the latest version from PyPI."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["info"]["version"]
    except requests.RequestException as e:
        print(f"Error fetching {package_name}: {e}")
        return None

def run_uv_add(args):
    """Run uv add command and refresh cache on failure once."""
    result = subprocess.run(["uv", "add"] + args)
    if result.returncode == 0:
        return True

    print("Initial add failed, attempting to refresh cache and retry...")

    # Refresh cache
    subprocess.run(["uv", "cache", "clean"], check=False)

    # Retry once
    result = subprocess.run(["uv", "add"] + args)
    return result.returncode == 0


def add_package(package_name):
    """Add the latest version of a package using uv."""
    version = get_latest_version(package_name)
    if version:
        print(f"Adding {package_name}>={version}...")
        success = run_uv_add([f"{package_name}>={version}"])
        if not success:
            raise RuntimeError(f"Failed to add {package_name} after cache refresh")
    else:
        print(f"Skipping {package_name} (no version found)")
        
        
def add_package_dev(package_name):
    """Add the latest version of a dev package using uv."""
    version = get_latest_version(package_name)
    if version:
        print(f"Adding {package_name}>={version} as dev dependency...")
        success = run_uv_add(["--dev", f"{package_name}>={version}"])
        if not success:
            raise RuntimeError(f"Failed to add dev {package_name} after cache refresh")
    else:
        print(f"Skipping {package_name} (no version found)")


def main():
    
    dev_packages = ["mikro-next", "alpaka", "kraph", "fluss-next", "reaktion-next", "lovekit", "unlok-next"]
    packages = ["rekuest-next", "kabinet", "turms", "fakts-next", "rath", "koil", "dokker"]
    
    
    
    for package in packages:
        add_package(package)
        
    for dev_package in dev_packages:
        add_package_dev(dev_package)

if __name__ == "__main__":
    
    
    
    
    
    main()
