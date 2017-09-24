# -*- mode: python -*-

block_cipher = None


a = Analysis(['pyimg.py'],
             pathex=['C:\\Users\\Administrator\\PyImg'],
             binaries=[],
             datas=[
				(r'C:\Users\Administrator\AppData\Local\Programs\Python\Python35\Lib\site-packages\tld\res', r'tld\res'),
			 ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          Tree('phantomjs-2.1.1-windows'),
          a.zipfiles,
          a.datas,
          name='pyimg',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
