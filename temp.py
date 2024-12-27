import win32com.client
import pythoncom
 
pcbApp = win32com.client.gencache.EnsureDispatch('MGCPCB.Application')
pcbDoc = win32com.client.Dispatch(pcbApp.ActiveDocument)
 
key = pcbDoc.Validate(0)
 
def validate(key):
    licenseServer = win32com.client.gencache.EnsureDispatch("MGCPCBAutomationLicensing.Application")
    # licenseServer = win32com.client.Dispatch("MGCPCBAutomationLicensing.Application")
    licenseToken = licenseServer.GetToken(key)
    pcbDoc.Validate(licenseToken)
    licenseServer = None
 
validate(key)
 
global g_clk_count
 
g_clk_count = 0
 
class EventHandler():
    def OnPreOnMouseClk(self, eButton, eFlags, dX, dY):
        global g_clk_count
        print('On Pre On Mouse Clk')
        print(eButton)
        print(eFlags)
        print(dX)
        print(dY)
        print('done')
        g_clk_count += 1
        print(g_clk_count)
 
CommandListener = pcbApp.Gui.CommandListener
 
handler = win32com.client.DispatchWithEvents(CommandListener, EventHandler)
 
keepOpen = True
 
while g_clk_count < 5:
    pythoncom.PumpWaitingMessages()
 
handler = None