# VDM++ Model of a Password Manager

This project implements a VDM++ model of a password manager. The model can be found in the folder `src` and if the VS Code Extension [VDM VSCode](https://marketplace.visualstudio.com/items?itemName=overturetool.vdm-vscode) is used then it is recommended to run VC Code from the folder `src` when using the model.

## Building the report

To generate the files for the appendix run the command bellow from root of the repository. (This uses the coverage files generate by the VDM VSCode extension. It looks for them in `src/.generated/coverage` and not in `.generated/coverage/src` therefore run VS Code from `src` when using the model.)

```PowerShell
$ python .\Helpers\generateTable.py
```

**NB: Right now the `generateTable.py` script is very rudimentary and uses the first coverage files it finds in `src/.generated/coverage` and not necessarily the newest. Therefore when generating the coverage files make sure to clear this folder first.**

After this the report can be build by building `latex/main.tex`. If using powerShell a helper script `latex/compile.ps1` can alternately be run that uses `PDFLatex` and `biber`.
