"""Encrypt or decrypt every PDF in folder and subfolder from
commandline using provided password.

Will add or remove the suffix _paranoia_encrypted to each filename

Will delete unencrypted files after encrypting and vice-versa

Functions:
    fuzzy_match(str, list) -> str | None
    fuzzy_input(list, str) -> Any
    get_folders(str) -> list
    choose_folder(list) -> path
    extensions_in_directories(path) -> iterable
    filestem_adder(str) -> str
    filestem_remover(str) -> str

TODO: Add docstrings for filestem functions
Work-out better structure/logic for the en/decryption pathways
"""
import argparse
import difflib
import logging
import PyPDF2
from pathlib import Path
from typing import Any, Iterable, List, Optional

logging.basicConfig(
    filename="pdfparanoia_DEBUG.txt",
    level=logging.DEBUG,
    format=" %(asctime)s - %(levelname)s - %(message)s",
)
#logging.disable(logging.CRITICAL)

parser = argparse.ArgumentParser(
    description="Encrypt or decrypt every PDF in folder and subfolder from commandline using provided password."
)
parser.add_argument("folder", help="Main folder to target, subfolders will also be decrypted")
parser.add_argument("password", help="For encrypting [if possible] all found pdfs")
args = parser.parse_args()

def fuzzy_match(name: str, names: List[str]) -> Optional[str]:
    """Return the closest match from a list of matches, also accept index"""
    try:
        number = int(name) - 1
    except ValueError:
        if matches := difflib.get_close_matches(name, names, n=1):
            return matches[0]
        return None

    return names[number] if 0 <= number < len(names) else None


def fuzzy_input(choices: List[Any], prompt: str = "Options:") -> Any:
    """Return user choice from choices"""
    print(prompt)
    print("\n".join(f"{i+1}. {choice}" for i, choice in enumerate(choices)))
    question = "\nPick an option from the list above (return to exit)\n > "
    while answer := input(question):
        if (match := fuzzy_match(answer, choices)) is not None:
            return match
    return None


def get_folders(
    name: str, directory: Optional[Path] = None, recursive=True
) -> List[Path]:
    """Return list of of folder paths of name in a directory [default: user]"""
    if directory is None:
        directory = Path.home()
    if recursive:
        files_and_folders = directory.rglob(name)
    else:
        files_and_folders = directory.glob(name)
    return [path for path in files_and_folders if path.is_dir()]


def choose_folder(folder_paths: List[Path]) -> Optional[Path]:
    """Prompt user to choose if multiple path options exist"""
    if not folder_paths:
        print("No such folder exists, buddy.\n")
        return None
    if len(folder_paths) == 1:
        return folder_paths[0]
    if (match := fuzzy_input(
        [x for x in folder_paths],
        prompt="You have multiple folders with that name. Choose one of them."
    )) is None:
        return None
    return match

def extensions_in_directories(directory: Path, extension: str) -> Iterable[Path]:
    """Returns every file with the correct extension in directory plus
    subdirectories.
    """
    yield from directory.rglob(f"*{extension}")


def filestem_adder(filename: str, text: str) -> str:
    filepath = Path(filename)
    new_filename = f"{filepath.stem}{text}{filepath.suffix}"
    return new_filename

def filestem_remover(filename: str, text: str) -> str:
    filepath = Path(filename)
    if not filepath.name.endswith(text):
        print(f"{filepath.name} does not end in {text}.")
        return filepath.name
    text_start_index = len(filepath.name)-len(text)
    new_filename = f"{filepath.name[0:text_start_index]}{filepath.suffix}"
    return new_filename

def main():
    directory = choose_folder(get_folder(args.folder))
    for pdf in extensions_in_directories(directory, "pdf"):
        was_encrypted = False
        with open(pdf, 'rb') as input_pdf:
            pdf_reader = PyPDF2.PdfFileReader(input_pdf)
            pdf_writer = PyPDF2.PdfFileWriter()
            if pdf_reader.isEncrypted:
                was_encrypted = True
                pdf_reader.decrypt(args.password)
            for page_num in range(pdf_reader.numPages):
                try:
                    pdf_writer.addPage(pdf_reader.getPage(page_num))
                except PdfReadError:
                    print(f"{args.password} didn't unlock {pdf.name}. Skipping..."})
                    break
            if not was_encrypted:
                pdf_writer.encrypt(args.password)
            #TODO: make a new file name based on if was_encrypted or not
            if pdf_writer.getNumPages() > 0:
                #check if there's actually content in the file to create a new pdf
                with open(new_filename, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
        logging.debug(f"{pdf} was encrypted? {was_encrypted}")
        #TODO: the new pdf checks, delete the old pdfs. Use the was_encrypted flag

if __name__ = "__main__":
    main()
