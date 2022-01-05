# auto_revision
This script helps convert screenshots made by GoG_bot to csv table. Each of every line contain account name and count of different resources.

## Requirements  
Testing with next environment:
- python 3.8.11
- tesseract v5.0.0-alpha.20201127
- pytesseract 0.3.8
- opencv 4.0.1

## Steps  
1. git clone `git clone https://github.com/dginozator/auto_revision`
2. Send files from gog_bot directory `src` to script directory `src`
3. Make sure that there are only images and only new ones in the folder.
4. Check out tesseract path on your PC and copy it's path to `t.py` file.
5. Launch script from directory `revision`:

```
python t.py
```

Result will be in main directory:
- csv file;
- image - for manual check result.
