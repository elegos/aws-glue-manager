# -*- mode: python ; coding: utf-8 -*-

from os import path
import glob
import platform
import shutil

import PyInstaller.config

system = platform.system().lower()
distPath = path.sep.join(['.', 'dist', system])
appName = 'AWSGlueManager'

PyInstaller.config.CONF['distpath'] = distPath

block_cipher = None

icons = glob.glob('./ui/icons/*.svg', recursive=True)

a = Analysis(['main.py'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=appName,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name=appName)


iconsInput = path.sep.join(['ui', 'icons'])
iconsOutput = path.sep.join([distPath, appName, 'ui', 'icons'])

shutil.rmtree(iconsOutput, True)
shutil.copytree(iconsInput, iconsOutput)
