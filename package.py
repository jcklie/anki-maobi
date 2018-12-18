import os
from zipfile import ZipFile

def copy_file_to_zip(myzip: ZipFile, source_path: str):
    """ Copies a file existing on disk `source_path` to the root of the zip file `myzip` """

    target_path = os.path.basename(source_path)

    with open(source_path, "rb") as source, myzip.open(target_path, 'w') as target:
        target.write(source.read())

if __name__ == "__main__":
    here = os.path.abspath(os.path.dirname(__file__))
    maobi = "maobi"

    about = {}
    with open(os.path.join(here, "maobi", "__version__.py")) as f:
        exec(f.read(), about)

    version = about["__version__"]

    package_name = f"maobi-{version}.zip"

    with ZipFile(package_name, 'w') as myzip:
        copy_file_to_zip(myzip, os.path.join(here, maobi, "__init__.py"))
        copy_file_to_zip(myzip, os.path.join(here, maobi, "__version__.py"))

        copy_file_to_zip(myzip, os.path.join(here, maobi, "characters.zip"))
        copy_file_to_zip(myzip, os.path.join(here, maobi, "hanzi-writer.min.js"))

        copy_file_to_zip(myzip, os.path.join(here, maobi, "config.json"))
        copy_file_to_zip(myzip, os.path.join(here, maobi, "config.md"))
                
        copy_file_to_zip(myzip, "LICENSE.txt")