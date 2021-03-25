from os import access
import logging
from ui.alertDialog import QAlertDialog
from PyQt5.QtCore import QObject, pyqtSignal
from lib.config import AWSProfile, ConfigManager
from PyQt5.QtWidgets import QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


class SettingsSignals(QObject):
    profilesModified = pyqtSignal()


class QProfileEditDialog(QDialog):
    originalLabel: str

    _logger: logging.Logger

    buttonBox: QDialogButtonBox
    label: QLineEdit
    region: QLineEdit
    accessKey: QLineEdit
    secretAccessKey: QLineEdit

    def __init__(self, title: str, label: str, region: str, accessKey: str, secretAccessKey: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setWindowTitle(title)
        self.setMinimumWidth(420)
        self._logger = logging.getLogger()

        self.originalLabel = label

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.label = QLineEdit(label)
        self.region = QLineEdit(region)
        self.accessKey = QLineEdit(accessKey)
        self.secretAccessKey = QLineEdit(secretAccessKey)

        formLayout = QFormLayout()
        formLayout.addRow(QLabel('Label:'), self.label)
        formLayout.addRow(QLabel('Region:'), self.region)
        formLayout.addRow(QLabel('AccessKey:'), self.accessKey)
        formLayout.addRow(QLabel('SecretAccessKey:'), self.secretAccessKey)

        form = QGroupBox()
        form.setLayout(formLayout)

        layout = QVBoxLayout()
        layout.addWidget(form)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class QSettingsDialog(QDialog):
    config: ConfigManager
    profilePicklist: QComboBox
    editButton: QPushButton
    deleteButton: QPushButton
    newButton: QPushButton

    signals: SettingsSignals

    _logger: logging.Logger

    def __init__(self, configManager: ConfigManager, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._logger = logging.getLogger()

        self.setWindowTitle('Settings')
        self.signals = SettingsSignals()

        self.config = configManager

        self.profilePicklist = QComboBox()
        self.populateProfilesPicklist()

        self.editButton = QPushButton('Edit')
        self.deleteButton = QPushButton('Delete')
        self.newButton = QPushButton('New')

        self.newButton.clicked.connect(self.onNewProfile)
        self.editButton.clicked.connect(self.onProfileEdit)
        self.deleteButton.clicked.connect(self.onProfileDelete)

        profilesLabel = QLabel('Profiles')

        layout = QVBoxLayout()
        layout.addWidget(profilesLabel)
        layout.addWidget(self.profilePicklist)

        buttonsWidget = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(self.editButton)
        buttonsLayout.addWidget(self.deleteButton)
        buttonsLayout.addWidget(self.newButton)
        buttonsWidget.setLayout(buttonsLayout)
        layout.addWidget(buttonsWidget)

        loadDataOnTabChangeCheckbox = QCheckBox('Load data on tab change')
        loadDataOnTabChangeCheckbox.setChecked(
            self.config.settings.loadDataOnTabChange)
        loadDataOnTabChangeCheckbox.toggled.connect(
            self.onLoadDataOnTabChangeToggled)
        layout.addWidget(loadDataOnTabChangeCheckbox)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accepted)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

        self.manageProfileButtonStates()

    def manageProfileButtonStates(self) -> None:
        if self.profilePicklist.count() == 0:
            self.editButton.setEnabled(False)
            self.deleteButton.setEnabled(False)
        else:
            self.editButton.setEnabled(True)
            self.deleteButton.setEnabled(True)

    def populateProfilesPicklist(self) -> None:
        self.profilePicklist.clear()
        self.profilePicklist.addItems(
            [profile.label for profile in self.config.settings.profiles])

    def onNewProfile(self, *args) -> None:
        dialog = QProfileEditDialog(
            title='New profile', label='', region='', accessKey='', secretAccessKey='')

        dialog.buttonBox.rejected.connect(lambda: dialog.close())
        dialog.buttonBox.accepted.connect(lambda: self.onProfileChange(dialog))

        dialog.exec_()

    def onProfileEdit(self, *args) -> None:
        profile: AWSProfile = next(
            (profile for profile in self.config.settings.profiles if profile.label == self.profilePicklist.currentText()))
        dialog = QProfileEditDialog(
            title='Edit profile', label=profile.label,
            region=profile.region, accessKey=profile.accessKey,
            secretAccessKey=profile.secretAccessKey
        )

        dialog.buttonBox.rejected.connect(lambda: dialog.close())
        dialog.buttonBox.accepted.connect(lambda: self.onProfileChange(dialog))

        dialog.exec_()

    def onProfileChange(self, dialog: QProfileEditDialog) -> None:
        profile = next(
            (profile for profile in self.config.settings.profiles if profile.label == dialog.originalLabel), None)
        found = profile is not None
        if not found:
            profile = AWSProfile()

        profile.label = dialog.label.text()
        profile.region = dialog.region.text()
        profile.accessKey = dialog.accessKey.text()
        profile.secretAccessKey = dialog.secretAccessKey.text()

        # New profile, add it to the list
        # otherwise the object will keep the changes
        if not found:
            self.config.settings.profiles.append(profile)
            self._logger.info(f'Created profile "{profile.label}"')
        else:
            self._logger.info(f'Edited profile "{profile.label}"')

        self.populateProfilesPicklist()
        self.manageProfileButtonStates()
        self.signals.settings.profilesModified.emit()

        dialog.close()

    def onProfileDelete(self, *args) -> None:
        profile: AWSProfile = next(
            (profile for profile in self.config.profiles if profile.label == self.profilePicklist.currentText()))

        dialog = QAlertDialog(
            f'Are you sure you want to delete profile "{profile.label}"?')
        dialog.accepted.connect(lambda: self.onProfileDeleted(profile))

        dialog.exec_()

    def onProfileDeleted(self, profile: AWSProfile) -> None:
        self.config.settings.profiles.pop(self.config.profiles.index(profile))
        self._logger.info(f'Deleted profile "{profile.label}"')

        self.populateProfilesPicklist()
        self.manageProfileButtonStates()
        self.signals.settings.profilesModified.emit()

    def onLoadDataOnTabChangeToggled(self, checked: bool) -> None:
        self.config.settings.loadDataOnTabChange = checked
