import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from GUI.PictureGUI import PictureGUI
import utils
import write
from copy import deepcopy
from xml.etree import ElementTree as ET


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.connect("delete-event", self.quit)

        self.set_border_width(10)
        self.set_default_size(700, 400)
        self.pArray = []
        self.pArray_bak = []
        self.noPhotosBox = None
        self.listboxPhotos = None
        self.sw = None
        self.propSW = None
        self.fileName = ""
        self.changed = False
        self.currentIndex = 0
        self.deleting_rows = False

        self.header_bar = Gtk.HeaderBar()
        self.header_bar.set_show_close_button(True)
        self.header_bar.props.title = "DDCreator"
        self.set_titlebar(self.header_bar)

        # open(xml) button on the left
        openButton = Gtk.Button(label="Open XML")
        openButton.connect("clicked", self.onOpenFile)
        self.header_bar.pack_start(openButton)

        # import(photos) button on the left
        importButton = Gtk.Button(label="Import Pictures")
        importButton.connect("clicked", self.onImportPhotos)
        self.header_bar.pack_start(importButton)

        # Save(xml) button on the right
        self.saveButton = Gtk.Button(label="Save")
        self.saveButton.connect("clicked", self.save)
        self.header_bar.pack_end(self.saveButton)

        # Save As(xml) button on the right
        self.saveasButton = Gtk.Button(label="Save As")
        self.saveasButton.connect("clicked", self.saveAs)
        self.header_bar.pack_end(self.saveasButton)

        # main box
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.add(self.mainBox)
        self.full_refresh()

    def full_refresh(self):
        if self.noPhotosBox is not None:
            self.noPhotosBox.destroy()
        if self.sw is not None:
            self.sw.destroy()
            self.sw = None
        if self.listboxPhotos is not None:
            self.listboxPhotos.destroy()
            self.listboxPhotos = None
        if self.propSW is not None:
            self.propSW.destroy()
            self.propSW = None
        if len(self.pArray) > 0:
            self.mainBox.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.sw = Gtk.ScrolledWindow()
            self.sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            self.mainBox.pack_start(self.sw, True, True, 0)
            self.addPhoto()
            self.addProperties()

            self.listboxPhotos.select_row(self.listboxPhotos.get_row_at_index(0))
        else:
            self.addNoPhotos()
        self.show_all()
        self.isChanged()
    def soft_refresh(self):
        if len(self.pArray) > 0:
            self.removeAllRows(self.listboxPhotos)
            self.show_all()
            self.addPhoto()
            self.listboxPhotos.select_row(self.listboxPhotos.get_row_at_index(self.currentIndex))
        else:
            self.full_refresh()

    def addPhoto(self):
        if self.listboxPhotos is None:
            self.listboxPhotos = Gtk.ListBox()
            #self.listboxPhotos.connect("row-selected", self.loadProperties)
            self.listboxPhotos.connect("row-activated", self.loadProperties)
            self.listboxPhotos.set_selection_mode(Gtk.SelectionMode.BROWSE)
            self.sw.add(self.listboxPhotos)

        for i in self.pArray:
            self.listboxPhotos.add(i.addPic())

        self.show_all()

    def removeAllRows(self, listbox):
        self.deleting_rows = True
        i = 0
        while True:
            row = listbox.get_row_at_index(0)
            if row is not None:
                row.destroy()
                i += 1
            else:
                break

        self.deleting_rows = False
    def addNoPhotos(self):
        self.mainBox.set_orientation(Gtk.Orientation.VERTICAL)

        self.noPhotosBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.mainBox.pack_start(self.noPhotosBox, True, False, 0)

        noPhotosTitle = Gtk.Label()
        noPhotosTitle.set_markup("<big><big><big><big>No pictures yet!</big></big></big></big>")
        self.noPhotosBox.pack_start(noPhotosTitle, fill=True, expand=False, padding=10)

        noPhotosMessage = Gtk.Label()
        noPhotosMessage.set_markup("<big>To add them, click Import button and choose your pictures!</big>")
        self.noPhotosBox.pack_start(noPhotosMessage, fill=True, expand=False, padding=10)

    def addProperties(self):
        self.propSW = Gtk.ScrolledWindow()
        self.propSW.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.mainBox.pack_end(self.propSW, True, True, 0)

        propertiesBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.propSW.add(propertiesBox)

        propertiesLabel = Gtk.Label()
        propertiesLabel.set_markup("<big><big><big><b>Properties</b></big></big></big>")
        propertiesBox.pack_start(propertiesLabel, False, False, 0)

        propertiesBox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        propertiesBox.pack_start(propertiesBox2, False, False, 0)

        # time
        timeBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        timeLabel = Gtk.Label(label="Time:")
        self.timeInput = Gtk.Entry()
        self.timeInput.connect("activate", self.apply)
        self.timeInput.set_placeholder_text("Time in 24hr format(hh:mm)")
        self.timeInput.set_max_length(5)
        self.timeInput.set_alignment(0.5)  # its ratio from 0 to 1 how to right its aligned. 0,5 is center
        self.timeInput.connect("changed", self.changedProp)
        timeBox.pack_start(timeLabel, False, False, 10)
        timeBox.pack_start(self.timeInput, True, True, 10)
        propertiesBox2.pack_start(timeBox, False, False, 5)

        # transition
        transitionBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        transitionLabel = Gtk.Label(label="Transition:")
        self.transitionInput = Gtk.Entry()
        self.transitionInput.connect("activate", self.apply)
        self.transitionInput.set_placeholder_text("Duration in s")
        self.transitionInput.set_max_length(5)
        self.transitionInput.set_alignment(0.5)  # its ratio from 0 to 1 how to right its aligned. 0,5 is center
        self.transitionInput.connect("changed", self.changedProp)
        transitionBox.pack_start(transitionLabel, False, False, 10)
        transitionBox.pack_start(self.transitionInput, True, True, 10)
        propertiesBox2.pack_start(transitionBox, False, False, 5)

        # Apply and reset buttons
        applyBox = Gtk.Box(spacing=0)
        propertiesBox.pack_end(applyBox, False, False, 0)

        self.applyButton = Gtk.Button(label="Apply")
        self.applyButton.connect("clicked", self.apply)
        self.applyButton.set_sensitive(False)
        applyBox.pack_start(self.applyButton, True, True, 10)

        self.restoreButton = Gtk.Button(label="Restore")
        self.restoreButton.connect("clicked", self.restore)
        self.restoreButton.set_sensitive(False)
        applyBox.pack_start(self.restoreButton, True, True, 5)
    def loadProperties(self, listbox, row):
        if not self.deleting_rows:
            currentPic = self.pArray[row.get_index()]
            self.currentIndex = row.get_index()
            self.timeInput.set_text(currentPic.picture.strTime)
            self.transitionInput.set_text(str(currentPic.picture.transition))
    def changedProp(self, widget):
        # first check if strings are valid
        self.isValid()

        # if its something to apply, make Apply clickable, otherwise make it not clickable
        if (self.pArray[self.currentIndex].picture.strTime != self.timeInput.get_text()) or (
                str(self.pArray[self.currentIndex].picture.transition) != self.transitionInput.get_text()
        ):
            if (self.timeInput.get_text() != "") and (self.transitionInput.get_text() != ""):
                self.applyButton.set_sensitive(True)
            self.restoreButton.set_sensitive(True)
        else:
            self.applyButton.set_sensitive(False)
            self.restoreButton.set_sensitive(False)

    def isValid(self):
        if not utils.isTimeValid(self.timeInput.get_text()):
            self.timeInput.set_text(self.timeInput.get_text()[:-1])

        digits = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'}
        if not digits.issuperset(self.transitionInput.get_text()):
            if self.transitionInput.get_text()[-1] == ',':
                self.transitionInput.set_text(self.transitionInput.get_text()[:-1] + '.')

    def apply(self, widget):
        self.pArray[self.currentIndex].picture.strTime = self.timeInput.get_text()
        self.pArray[self.currentIndex].picture.transition = str(float(self.transitionInput.get_text()))
        self.applyButton.set_sensitive(False)
        self.restoreButton.set_sensitive(False)
        self.soft_refresh()
        self.isChanged()
    def restore(self, widget):
        self.timeInput.set_text(self.pArray[self.currentIndex].picture.strTime)
        self.transitionInput.set_text(str(self.pArray[self.currentIndex].picture.transition))
        self.applyButton.set_sensitive(False)

    def onImportPhotos(self, widget):
        dialog = Gtk.FileChooserDialog(title="Import Picture(s)", parent=self, action=Gtk.FileChooserAction.OPEN)
        dialog.set_select_multiple(True)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
                           "Import", Gtk.ResponseType.OK)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            pending = dialog.get_filenames()
            while len(pending) > 0:
                p = PictureGUI(path=pending[0], strTime="21:37",
                               transition=float(5))
                self.pArray.append(p)
                pending = pending[1:]
            if self.sw is None: #if there is noPictures screen
                self.full_refresh() #create list
            else:
                self.soft_refresh() #only modify list
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

    def onOpenFile(self, widget):
        if self.changed:
            dialog = Gtk.MessageDialog(parent=self, flags=0, message_type=Gtk.MessageType.QUESTION,
                                       buttons=Gtk.ButtonsType.YES_NO, text="Are you sure?")
            dialog.format_secondary_text(
                "There is unsaved session running. Do you want to continue?(it will delete all your changes!)")
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                dialog.destroy()
            elif response == Gtk.ResponseType.NO:
                dialog.destroy()
                return

        dialog = Gtk.FileChooserDialog(title="Open XML file", parent=self, action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
                           "Open", Gtk.ResponseType.OK)

        _filter = Gtk.FileFilter()
        _filter.set_name("XML Files")
        _filter.add_pattern("*.xml")
        dialog.add_filter(_filter)
        _filter = Gtk.FileFilter()
        _filter.set_name("All Files")
        _filter.add_pattern("*")
        dialog.add_filter(_filter)

        response = dialog.run()
        if (response == Gtk.ResponseType.OK):
            print("File selected: " + dialog.get_filename())
            self.fileName = dialog.get_filename()
            self.pArray = self.importXml(self.fileName)
            self.pArray_bak = self.importXml(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("rabini są niezdecydowani")

        dialog.destroy()
        self.full_refresh()
    def importXml(self, file):
        sumSecTime = 0
        myList = []
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            for i in range(len(root.findall('.//static'))):
                static = root.findall('.//static')[i]
                transition = root.findall('.//transition')[i]

                secTime = int(float(static.find('duration').text))
                sumSecTime += secTime

                minutes = sumSecTime / 60
                hours = 0
                while (minutes > 59):
                    minutes -= 60
                    hours += 1

                if hours < 10:
                    hours = "0" + str(int(hours))
                if minutes < 10:
                    minutes = "0" + str(int(minutes))
                strTime = "%s:%s" % (str(hours), str(minutes))

                p = PictureGUI(path=static.find('file').text, strTime=strTime,
                               transition=float(transition.find('duration').text))
                myList.append(p)
        except:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
                                       Gtk.ButtonsType.YES_NO, "Something went wrong!")
            dialog.format_secondary_text(
                "Your file is probably corrupted. Make sure your file is correct.\nDo you want to show what has been loaded before crash?")
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                dialog.destroy()
                return myList
            elif response == Gtk.ResponseType.NO:
                dialog.destroy()
                return self.pArray
        self.header_bar.props.title = "%s%s - DDCreator" % ("", utils.pathToFileName(self.fileName))
        self.set_titlebar(self.header_bar)
        return myList

    def save(self, widget):
        if self.changed:
            write.write(picArray=self.pArray, name=self.fileName)
            self.pArray_bak = deepcopy(self.pArray)
            self.isChanged()
            self.full_refresh()
    def saveAs(self, widget):
        dialog = Gtk.FileChooserDialog(title="Open XML file", parent=self, action=Gtk.FileChooserAction.SAVE)
        dialog.set_current_name("Untitled")
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
                           "Save As", Gtk.ResponseType.APPLY)
        filter = Gtk.FileFilter()
        filter.set_name("Text Files")
        filter.add_mime_type("text/xml")
        dialog.add_filter(filter)
        Gtk.FileChooser.set_do_overwrite_confirmation(dialog, True)
        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            self.fileName = dialog.get_filename()
            self.save(widget)
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
        dialog.destroy()

    def isChanged(self):

        self.changed = utils.compare_pArrays(self.pArray, self.pArray_bak)

        if self.fileName != "":
            if self.changed:
                self.saveasButton.set_sensitive(True)
                self.saveButton.set_sensitive(True)
                self.header_bar.props.title = "%s%s - DDCreator" % ("*", utils.pathToFileName(self.fileName))
            else:
                self.saveasButton.set_sensitive(True)
                self.saveButton.set_sensitive(False)
                self.header_bar.props.title = "%s%s - DDCreator" % ("", utils.pathToFileName(self.fileName))
        else:
            if len(self.pArray) > 0:
                if self.changed:
                    self.saveButton.set_sensitive(False)
                    self.saveasButton.set_sensitive(True)
                    self.header_bar.props.title = "* Untitled.xml - DDCreator"
                else:
                    self.saveButton.set_sensitive(False)
                    self.saveasButton.set_sensitive(False)
                    self.header_bar.props.title = "Untitled.xml - DDCreator"
            else:
                self.saveButton.set_sensitive(False)
                self.saveasButton.set_sensitive(False)
                self.header_bar.props.title = "DDCreator"
        self.set_titlebar(self.header_bar)

        return self.changed

    def quit(self, widget, event):
        if self.changed:
            dialog = Gtk.MessageDialog(parent=self, flags=0, message_type=Gtk.MessageType.QUESTION, text="Are you sure?")
            dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
                               "Save", Gtk.ResponseType.OK,
                               "Save As", Gtk.ResponseType.APPLY,
                               "Exit", Gtk.ResponseType.YES,)
            dialog.format_secondary_text(
                "There is unsaved session running. Do you want to continue?(it will delete all your changes!)")
            response = dialog.run()
            if response == Gtk.ResponseType.YES:    #Close
                dialog.destroy()
                Gtk.main_quit()
            elif response == Gtk.ResponseType.OK:   #Save
                self.save(None)
                dialog.destroy()
                Gtk.main_quit()
            elif response == Gtk.ResponseType.APPLY: #Save As
                self.saveAs(None)
                dialog.destroy()
                Gtk.main_quit()
            dialog.destroy()
            return True
        else:
            Gtk.main_quit()


window = MainWindow()
window.show_all()
Gtk.main()
