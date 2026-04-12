import sys
import pythoncom
pythoncom.CoInitialize()
sys.path.insert(0, r"D:\sw2026\SolidworksMCP-python\src")
try:
    import win32com.client
    sw = win32com.client.GetActiveObject("SldWorks.Application")
    print("COM connected:", type(sw))
    rev = sw.RevisionNumber
    print("SW Revision:", rev)
    doc = sw.ActiveDoc
    print("ActiveDoc type:", type(doc))
    if doc:
        title = doc.GetTitle
        print("Active doc title:", title)
    else:
        print("No active document")
except Exception as e:
    import traceback
    print("ERROR:", type(e).__name__, str(e))
    traceback.print_exc()
finally:
    pythoncom.CoUninitialize()
