import win32com.client as win32

class PCBEventHandler:
    def __init__(self):
        self.app = win32.gencache.EnsureDispatch("MGCPCB.ExpeditionPCBApplication")
        self.doc = self.app.ActiveDocument

    def OnSave(self, *args):
        self.log_event('Save event triggered.')
        self.handle_save_event()

    def OnSelectionChange(self, *args):
        self.log_event('Selection change event triggered.')

    def OnClick(self, *args):
        self.log_event('Print X, Y position')
        

    def log_event(self, message):
        print(message)
        # 파일에 로그를 저장할 수도 있음
        with open("./logs/event_log.txt", "a") as log_file:
            log_file.write(f"{message}\n")

    def handle_save_event(self):
        try:
            nets = self.doc.Nets
            file_name = f"nets.txt"

            with open("./logs/" + file_name, "w") as file:
                for net in nets:
                    file.write(f"{net.Name}\n")

            print(f"Nets saved to {file_name}")

        except Exception as e:
            print(f"Error handling save event: {e}")