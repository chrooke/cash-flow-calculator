#!/usr/bin/env python
import os
import wx
import wx.adv
from datetime import date, timedelta
from cash_flow.transaction import Transaction
from cash_flow.transaction_store import TransactionStore
from cash_flow.cash_flow import CashFlow


class CashFlowDisplay(wx.Panel):
    def __init__(self, parent, ts):
        super().__init__(parent)
        self.ts = ts
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)
        self.tempDrawSomething()

    def tempDrawSomething(self):
        self.main_sizer.Clear()
        for t in self.ts.getTransactions():
            label = f'{t.description} {t.amount} {t.start}'
            txt = wx.StaticText(self, label=label)
            self.main_sizer.Add(txt,0)
            self.main_sizer.Layout()


class TransactionManagement(wx.Panel):
    def __init__(self, parent, ts):
        super().__init__(parent)
        self.ts = ts
        self.editPane1 = None
        self.transaction_buttons = {}
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.left_side_sizer = wx.BoxSizer(wx.VERTICAL)
        self.t_list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.left_side_sizer.Add(self.t_list_sizer, 0)
        btn = wx.Button(self, label='New Transaction')
        btn.Bind(wx.EVT_BUTTON, self.newTransaction)
        self.left_side_sizer.Add(btn, 0)
        self.main_sizer.Add(self.left_side_sizer, 0)
        self.SetSizer(self.main_sizer)

    def redraw(self):
        self.clearEditPane()
        self.rebuildTransactionButtons()

    def clearEditPane(self):
        if self.main_sizer.GetItemCount() > 1:
            self.main_sizer.Remove(1)
            if self.editPane1:
                self.editPane1.Destroy()
                self.editPane1 = None
            self.main_sizer.Layout()

    def rebuildTransactionButtons(self):
        self.t_list_sizer.Clear()
        for t in self.transaction_buttons:
            self.transaction_buttons[t].Destroy()
        self.transaction_buttons = {}
        for t in self.ts.getTransactions():
            self.updateButtonForTransaction(t)
        self.main_sizer.Layout()

    def editTransaction(self, event, trans):
        self.clearEditPane()
        self.editPane1 = EditTransactionPanel(self, trans)
        self.main_sizer.Add(self.editPane1, 0)
        self.main_sizer.Layout()

    def newTransaction(self, event):
        t = Transaction()
        self.editTransaction(event, t)

    def deleteTransaction(self, trans):
        self.ts.removeTransactions(trans)
        self.rebuildTransactionButtons()

    def updateButtonForTransaction(self, t):
        label = f'{t.description} {t.amount} {t.start}'
        if t in self.transaction_buttons:
            btn = self.transaction_buttons[t]
            btn.SetLabel(label)
        else:
            btn = wx.Button(self, label=label)
            btn.Bind(wx.EVT_BUTTON, lambda evt, trans=t: self.editTransaction(evt, trans))
            self.t_list_sizer.Add(btn, 0)
            self.transaction_buttons[t] = btn
        if t not in self.ts.getTransactions():
            self.ts.addTransactions(t)
        self.t_list_sizer.Layout()


class EditTransactionPanel(wx.Panel):
    def __init__(self, parent, trans):
        super().__init__(parent)
        self.parent = parent
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.transaction = trans

        # Description

        self.description = wx.TextCtrl(self)
        self.main_sizer.Add(self.description, 0, wx.EXPAND)

        # Date
        label = wx.StaticText(self, label='Date', size=(50, -1))
        self.start = wx.adv.DatePickerCtrl(self)
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(label, 0, wx.ALL, 5)
        row_sizer.Add(self.start, 1, wx.ALL, 5)
        self.main_sizer.Add(row_sizer, 0)

        # Amount
        label = wx.StaticText(self, label='Amount', size=(50, -1))
        self.amount = wx.TextCtrl(self)
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(label, 0, wx.ALL, 5)
        row_sizer.Add(self.amount, 1, wx.ALL, 5)
        self.main_sizer.Add(row_sizer, 0)

        # Frequency
        label = wx.StaticText(self, label='Frequency', size=(50, -1))
        self.frequency = wx.Choice(self, choices=Transaction.INTERVALS)
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(label, 0, wx.ALL, 5)
        row_sizer.Add(self.frequency, 1, wx.ALL, 5)
        self.main_sizer.Add(row_sizer, 0)

        # Scheduled
        self.scheduled = wx.CheckBox(self, label='Scheduled', style=wx.CHK_2STATE | wx.ALIGN_RIGHT)
        self.main_sizer.Add(self.scheduled, 0)

        # Cleared
        self.cleared = wx.CheckBox(self, label='Cleared', style=wx.CHK_2STATE | wx.ALIGN_RIGHT)
        self.main_sizer.Add(self.cleared, 0)

        # Action Buttons
        action_button_sizer = wx.BoxSizer()

        cancel = wx.Button(self, label="Cancel")
        cancel.Bind(wx.EVT_BUTTON, self.cancelEdit)
        action_button_sizer.Add(cancel, 0)

        reset = wx.Button(self, label="Reset")
        reset.Bind(wx.EVT_BUTTON, self.resetEdit)
        action_button_sizer.Add(reset, 0)

        save = wx.Button(self, label="Save")
        save.Bind(wx.EVT_BUTTON, self.saveEdit)
        action_button_sizer.Add(save, 0)

        self.main_sizer.Add(action_button_sizer, 0)

        # Delete Button
        delete_button_sizer = wx.BoxSizer()
        delete = wx.Button(self, label="Delete")
        delete.Bind(wx.EVT_BUTTON, self.deleteTransaction)
        delete_button_sizer.Add(delete, 0)

        self.main_sizer.Add(delete_button_sizer, 0)

        self.setValues()

        self.SetSizer(self.main_sizer)

    def setValues(self):
        self.description.SetValue(self.transaction.description)
        tdate = wx.DateTime(self.transaction.start.day, self.transaction.start.month-1, self.transaction.start.year)
        self.start.SetValue(tdate)
        self.amount.SetValue(str(self.transaction.amount))
        self.frequency.SetSelection(Transaction.INTERVALS.index(self.transaction.frequency))
        self.scheduled.SetValue(self.transaction.scheduled)
        self.cleared.SetValue(self.transaction.cleared)

    def cancelEdit(self, event):
        self.parent.clearEditPane()

    def resetEdit(self, event):
        self.setValues()

    def saveEdit(self, event):
        self.transaction.description = self.description.GetValue()
        wxDate = self.start.GetValue()
        new_date = date(wxDate.GetYear(), wxDate.GetMonth()+1, wxDate.GetDay())
        self.transaction.updateStartDate(new_date)
        self.transaction.amount = self.amount.GetValue()
        self.transaction.frequency = Transaction.INTERVALS[self.frequency.GetCurrentSelection()]
        self.transaction.scheduled = self.scheduled.GetValue()
        self.transaction.cleared = self.cleared.GetValue()
        self.parent.updateButtonForTransaction(self.transaction)
        self.parent.clearEditPane()

    def deleteTransaction(self, event):
        self.parent.deleteTransaction(self.transaction)
        self.parent.clearEditPane()


class MainFrame(wx.Frame):
    WILDCARD = "YAML (*.yml)|*.yml|"     \
               "All files (*.*)|*.*"

    def __init__(self):
        super().__init__(parent=None, title='Cash Flow Calculator')
        self.ts = TransactionStore()
        self.file = None
        self.notebook = wx.Notebook(self)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.handleNotebookChange)
        self.transactionManagement = TransactionManagement(self.notebook, self.ts)
        self.notebook.AddPage(self.transactionManagement, "Transaction Management")
        self.cashFlowDisplay = CashFlowDisplay(self.notebook, self.ts)
        self.notebook.AddPage(self.cashFlowDisplay, "Cash Flow")
        self.SetInitialSize(wx.Size(500, 800))
        self.create_menu()
        self.Show()

    def handleNotebookChange(self, event):
        self.updateChildren()
        event.Skip()

    def updateChildren(self):
        self.transactionManagement.redraw()
        self.cashFlowDisplay.tempDrawSomething()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        new_file_menu_item = file_menu.Append(
            wx.ID_ANY, "New File", "Create a new file"
        )
        open_file_menu_item = file_menu.Append(
            wx.ID_ANY, "Open...", "Open a file"
        )
        save_menu_item = file_menu.Append(
            wx.ID_ANY, "Save", "Save to current file"
        )
        save_as_menu_item = file_menu.Append(
            wx.ID_ANY, "Save As", "Save file with new name"
        )
        menu_bar.Append(file_menu, "&File")
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_new_file,
            source=new_file_menu_item,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_open_file,
            source=open_file_menu_item,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_save,
            source=save_menu_item,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_save_as,
            source=save_as_menu_item,
        )
        self.SetMenuBar(menu_bar)

    def on_new_file(self, event):
        self.loadTransactions()

    def on_open_file(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=MainFrame.WILDCARD,
            style=wx.FD_OPEN |
                  wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST |
                  wx.FD_PREVIEW
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.loadTransactions(dlg.GetPath())
        dlg.Destroy()

    def on_save(self, event):
        if self.file is not None:
            self.saveTransactions()
        else:
            self.on_save_as(event)

    def on_save_as(self, event):
        if self.file is not None:
            defaultDir = os.path.dirname(self.file)
            defaultFile = os.path.basename(self.file)
        else:
            defaultDir = os.getcwd()
            defaultFile = ""
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=defaultDir,
            defaultFile=defaultFile, wildcard=MainFrame.WILDCARD, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.saveTransactions(dlg.GetPath())
        dlg.Destroy()

    def loadTransactions(self, file=None):
        self.ts = TransactionStore()
        if file is not None:
            self.ts.loadTransactions(file)
            self.file = file
        self.transactionManagement.ts = self.ts
        self.cashFlowDisplay.ts = self.ts
        self.updateChildren()

    def saveTransactions(self, file=None):
        if file is None:
            file = self.file
        self.file = file
        self.ts.saveTransactions(file)

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
