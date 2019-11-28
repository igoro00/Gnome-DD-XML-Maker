import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from GUI.PictureGUI import PictureGUI
import utils
import write
from xml.etree import ElementTree as ET


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.set_border_width(10)
        self.set_default_size(700, 400)
        self.pArray = []
        self.noPhotosBox = None
        self.sw = None
        self.propSW = None
        self.fileName = ""
        self.changed=False

        self.header_bar = Gtk.HeaderBar()
        self.header_bar.set_show_close_button(True)
        self.header_bar.props.title = "DDCreator"
        self.set_titlebar(self.header_bar)

        # open button on the right
        openButton = Gtk.Button(label="Open")
        openButton.connect("clicked", self.onOpenFile)
        self.header_bar.pack_start(openButton)

        # import(photos) button on the right
        importButton = Gtk.Button(label="Import Pictures")
        # importButton.connect("clicked", self.importPhotos)
        self.header_bar.pack_start(importButton)

        # main box
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.add(self.mainBox)
        self.refresh()

    def refresh(self):
        print(self.pArray)
        if self.noPhotosBox is not None:
            self.noPhotosBox.destroy()
        if self.sw is not None:
            self.sw.destroy()
        if self.propSW is not None:
            self.propSW.destroy()
        if len(self.pArray) > 0:
            self.mainBox.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.addPhoto()
            self.addProperties()
        else:
            self.addNoPhotos()
        self.show_all()

    def addPhoto(self):
        self.sw = Gtk.ScrolledWindow()
        self.sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listboxPhotos = Gtk.ListBox()
        self.listboxPhotos.connect("row-selected", self.loadProperties)
        self.listboxPhotos.set_selection_mode(Gtk.SelectionMode.BROWSE)

        for i in self.pArray:
            self.listboxPhotos.add(i.addPic())
        self.sw.add(self.listboxPhotos)
        self.mainBox.pack_start(self.sw, True, True, 0)
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
        self.transitionInput.set_placeholder_text("Duration in s")
        self.transitionInput.set_max_length(5)
        self.transitionInput.set_alignment(0.5)  # its ratio from 0 to 1 how to right its aligned. 0,5 is center
        self.transitionInput.connect("changed", self.changedProp)
        transitionBox.pack_start(transitionLabel, False, False, 10)
        transitionBox.pack_start(self.transitionInput, True, True, 10)
        propertiesBox2.pack_start(transitionBox, False, False, 5)

        # Apply and reset buttons
        applyBox = Gtk.Box(spacing=20)
        propertiesBox.pack_end(applyBox, False, False, 0)

        self.applyButton = Gtk.Button(label="Apply")
        self.applyButton.connect("clicked", self.apply)
        self.applyButton.set_sensitive(False)
        applyBox.pack_start(self.applyButton, False, False, 0)

        self.restoreButton = Gtk.Button(label="Restore")
        self.restoreButton.connect("clicked", self.restore)
        self.restoreButton.set_sensitive(False)
        applyBox.pack_start(self.restoreButton, False, False, 0)
    def loadProperties(self, listbox, row):
        currentPic = self.pArray[row.get_index()]
        self.currentIndex = row.get_index()
        print(currentPic.picture.strTime)
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
        self.pArray[self.currentIndex].picture.transition = self.transitionInput.get_text()
        self.changed = True
        self.header_bar.props.title = "%s%s - DDCreator" % ("*", utils.pathToFileName(self.fileName))
        self.set_titlebar(self.header_bar)
        self.applyButton.set_sensitive(False)
    def restore(self, widget):
        self.timeInput.set_text(self.pArray[self.currentIndex].picture.strTime)
        self.transitionInput.set_text(str(self.pArray[self.currentIndex].picture.transition))
        self.applyButton.set_sensitive(False)

    def onOpenFile(self, widget):
        if self.changed == True:
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


        dialog = Gtk.FileChooserDialog(title="Open file(s)", parent=self, action=Gtk.FileChooserAction.OPEN)
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
            self.pArray = self.importXml(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("rabini są niezdecydowani")

        dialog.destroy()
        self.refresh()
        self.listboxPhotos.select_row(self.listboxPhotos.get_row_at_index(0))
    def importXml(self, file):
        sumSecTime = 0
        myList = []
        self.fileName=file
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
        self.header_bar.props.title = "%s%s - DDCreator"%("", utils.pathToFileName(self.fileName))
        self.set_titlebar(self.header_bar)
        return myList

    def save(self):
        self.changed = False
        write.write(picArray=self.pArray, name=self.fileName)
        self.header_bar.props.title = "%s%s - DDCreator" % ("", utils.pathToFileName(self.fileName))
        self.set_titlebar(self.header_bar)
    def saveAs(self):
        #self.fileName = dialog that chooses new file
        self.save()



window = MainWindow()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
