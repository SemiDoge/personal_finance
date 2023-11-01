from .pdf import AssetPie2dp

if __name__ == "__main__":  # NORUNTESTS
    AssetPie2dp().save(formats=["pdf"], outDir=".", fnRoot=None)
