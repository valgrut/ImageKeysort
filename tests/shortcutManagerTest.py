import unittest
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QCoreApplication

from src.main import main
from src.MainWindow import MainWindow
from src.ShortcutManager import ShortcutManager


QCoreApplication.setOrganizationName("JP")
QCoreApplication.setOrganizationDomain("wogon.cz")
QCoreApplication.setApplicationName("Image Keysort")

app = QApplication([])  # needed for the app to work during testing

# Notes:
# - "test_" in the method name is required for unittest to recognize the test method

class TestShortcutManager(unittest.TestCase):
    def setUp(self):
        # Create the application window and button (the GUI to be tested)
        self.window = MainWindow()  # Replace with your actual window class
        self.sm = ShortcutManager(self.window)
        # self.galleryManager = self.window.galleryManager
        # self.button = self.window.copyButton  # Example: the button you're testing


    def test_getAllPaths_simple(self):
        # Example test for getAllPaths
        shortcutsData = {
            "keys": {
                "a": {
                    "dst_path": "",
                    "keys": {
                        "a": {
                            "dst_path": "C:/image-sorter/testing-data/kk",
                            "keys": {}
                        }
                    }
                }
            }
        }
        manager = ShortcutManager(self.window)
        paths = manager.getAllPaths(shortcutsData)

        # Check if the paths returned are as expected
        self.assertEqual(paths, ["C:/image-sorter/testing-data/kk"])


    def test_getAllPaths_complex(self):
        shortcutsData = {
            "keys": {
                "w": {
                    "dst_path": "HOME/Gaming/The Witcher",
                    "keys": {}
                },
                "o": {
                    "dst_path": "HOME/Gaming/World of Warcraft",
                    "keys": {}
                },
                "c": {
                    "dst_path": "HOME/Gaming/Cyberpunk 2077",
                    "keys": {}
                },
                "m": {
                    "dst_path": "HOME/Memes/Gaming memes",
                    "keys": {
                        "f": {
                            "dst_path": "HOME/Memes/Gaming memes/Factorio",
                            "keys": {}
                        },
                        "e": {
                            "dst_path": "HOME/Memes/Gaming memes/Path of Exile",
                            "keys": {}
                        },
                        "w": {
                            "dst_path": "HOME/Memes/Gaming memes/The Witcher",
                            "keys": {}
                        },
                        "o": {
                            "dst_path": "HOME/Memes/Gaming memes/WoW",
                            "keys": {}
                        }
                    }
                },
                "g": {
                    "dst_path": "HOME/Gaming/Guild wars 2",
                    "keys": {}
                }
            }
        }
        manager = ShortcutManager(self.window)
        paths = manager.getAllPaths(shortcutsData)

        # Check if the paths returned are as expected
        self.assertEqual(paths, ["HOME/Gaming/The Witcher", "HOME/Gaming/World of Warcraft", "HOME/Gaming/Cyberpunk 2077", "HOME/Memes/Gaming memes", "HOME/Memes/Gaming memes/Factorio", "HOME/Memes/Gaming memes/Path of Exile", "HOME/Memes/Gaming memes/The Witcher", "HOME/Memes/Gaming memes/WoW", "HOME/Gaming/Guild wars 2"])
        self.sm.clearShortcuts()


    # def test_toggleCoppyMode(self):
    #     # Check that copy mode is set to False
    #     self.assertEqual(self.window.copyOnly, False)  # Example assertion

    #     # Simulate clicking the button
    #     QTest.mouseClick(self.button, Qt.LeftButton)

    #     # Check if the button click did what it's supposed to do
    #     self.assertEqual(self.window.copyOnly, True)  # Example assertion


    # ========== addShortcut ==========
    def test_addShortcut_no_dst(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("a")
        self.assertIn('a', sm.shortcutTree['keys'])
        self.assertEqual(sm.areShortcutsModified(), True)


    def test_addShortcut_complex(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        expectedOutput = {
        "keys": {
            "a": {
            "dst_path": "",
            "keys": {
                "b": {
                "dst_path": "",
                "keys": {
                    "c": {
                    "dst_path": "",
                    "keys": {
                        "d": {
                        "dst_path": "",
                        "keys": {}
                        }
                    }
                    }
                }
                }
            }
            }
        }
        }

        actualOutput = sm.shortcutTree
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), True)


    def test_addShortcut_addExisting(self):
        # Prepare
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.setDataUnmodified()  # reset modified flag
        expectedOutput = {
        "keys": {
            "a": {
            "dst_path": "",
            "keys": {
                "b": {
                "dst_path": "",
                "keys": {
                    "c": {
                    "dst_path": "",
                    "keys": {
                        "d": {
                        "dst_path": "",
                        "keys": {}
                        }
                    }
                    }
                }
                }
            }
            }
        }
        }

        # Test
        sm.addShortcutSequence("ab")
        actualOutput = sm.shortcutTree
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    # ========== addKeyUnderCurrent ==========
    def test_addKeyUnderCurrent(self):
        pass


    # ========== updateDstPathForShortcut ==========
    def test_updateDstForShortcut_assign_dst(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")

        expectedOutput = {
        "keys": {
            "a": {
            "dst_path": "",
            "keys": {
                "b": {
                "dst_path": "",
                "keys": {
                    "c": {
                    "dst_path": "",
                    "keys": {
                        "d": {
                        "dst_path": "/home/user/Pictures/Photos",
                        "keys": {}
                        }
                    }
                    }
                }
                }
            }
            }
        }
        }

        actualOutput = sm.shortcutTree
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), True)


    def test_updateDstForShortcut_change_dst(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag
        expectedOutput = {
        "keys": {
            "a": {
            "dst_path": "",
            "keys": {
                "b": {
                "dst_path": "",
                "keys": {
                    "c": {
                    "dst_path": "",
                    "keys": {
                        "d": {
                        "dst_path": "/home/user/Pictures/Photos",
                        "keys": {}
                        }
                    }
                    }
                }
                }
            }
            }
        }
        }
        actualOutput = sm.shortcutTree
        self.assertEqual(actualOutput, expectedOutput)

        sm.updateDstPathForShortcut("abcd", "/home/user/Documents")
        actualOutput = sm.shortcutTree
        expectedOutput = {
        "keys": {
            "a": {
            "dst_path": "",
            "keys": {
                "b": {
                "dst_path": "",
                "keys": {
                    "c": {
                    "dst_path": "",
                    "keys": {
                        "d": {
                        "dst_path": "/home/user/Documents",
                        "keys": {}
                        }
                    }
                    }
                }
                }
            }
            }
        }
        }
        self.assertEqual(actualOutput, expectedOutput)
        # Changing dst for some shortcut should cause modified state to be True; TODO;
        self.assertEqual(sm.areShortcutsModified(), True)


    def test_updateDstForShortcut_nonexisting_shortcut(self):
        sm = ShortcutManager(self.window)
        expectedOutput = False
        actualOutput = sm.updateDstPathForShortcut("xyz", "/home/user/Pictures/Photos")
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    # ========== getDstForShortcut ==========
    def test_getDstForShortcut(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        expectedOutput = "/home/user/Pictures/Photos"

        actualOutput = sm.getDstPathForShortcut("abcd")
        self.assertEqual(actualOutput, expectedOutput)


    def test_getDstForShortcut_shortcut_does_not_exist(self):
        sm = ShortcutManager(self.window)
        expectedOutput = None
        actualOutput = sm.getDstPathForShortcut("xyz")

        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    def test_getDstForShortcut_dst_does_not_exist(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.setDataUnmodified()  # reset modified flag

        expectedOutput = None
        actualOutput = sm.getDstPathForShortcut("abcd")

        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    # ========== removeShortcutSequence ==========
    def test_removeShortcutSequence_remove_last(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        sm.removeShortcutSequence("abc-d")
        expectedOutput = {
        "keys": {
            "a": {
            "dst_path": "",
            "keys": {
                "b": {
                "dst_path": "",
                "keys": {
                    "c": {
                    "dst_path": "",
                    "keys": {}
                    }
                }
                }
            }
            }
        }
        }

        actualOutput = sm.shortcutTree
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), True)


    def test_removeShortcutSequence_remove_first(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        sm.removeShortcutSequence("-a")
        expectedOutput = {
        "keys": {}
        }

        actualOutput = sm.shortcutTree
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), True)


    def test_removeShortcutSequence_remove_all_but_first(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        sm.removeShortcutSequence("a-b")
        expectedOutput = {
        "keys": {
            "a": {
            "dst_path": "",
            "keys": {}
            }
        }
        }

        actualOutput = sm.shortcutTree
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), True)


    def test_removeShortcutSequence_wrong_syntax_too_many_chars_after(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        expectedOutput = sm.removeShortcutSequence("-abcd")
        actualOutput = False
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    def test_removeShortcutSequence_wrong_syntax(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        expectedOutput = False
        actualOutput = sm.removeShortcutSequence("abc-def")
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    def test_removeShortcutSequence_wrong_syntax_minus_only(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        expectedOutput = False
        actualOutput = sm.removeShortcutSequence("-")
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    def test_removeShortcutSequence_left_exists_right_not(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        expectedOutput = False
        actualOutput = sm.removeShortcutSequence("abc-x")
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    def test_removeShortcutSequence_right_exists_left_not(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        expectedOutput = False
        actualOutput = sm.removeShortcutSequence("xyz-d")
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    # ========== MoveShortcutSequence ==========
    def test_moveShortcutSequence_simple(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        sm.moveShortcutSequence("abcd>")
        expectedOutput = {
            "keys": {
                "a": {
                "dst_path": "",
                "keys": {
                    "b": {
                    "dst_path": "",
                    "keys": {
                        "c": {
                        "dst_path": "",
                        "keys": {}
                        }
                    }
                    }
                }
                },
                "d": {
                "dst_path": "/home/user/Pictures/Photos",
                "keys": {}
                }
            }
            }


        actualOutput = sm.shortcutTree
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), True)

    def test_moveShortcutSequence_move_subtree(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag

        sm.moveShortcutSequence("abc>")

        # TODO: Vsechny tyhle stromy zamenit za check, jeslti existuje ta
        # presunuta sekvence. Kdyz bych do json chtel neco pridat, musel bych
        # to pak vsude rucne upravovat:
        # actualOutput = sm.checkShortcutExists("c")  # Should be True
        # actualOutput = sm.checkShortcutExists("ab")  # Should be True
        # actualOutput = sm.checkShortcutExists("abc")  # Should be False

        expectedOutput = {
            "keys": {
                "a": {
                "dst_path": "",
                "keys": {
                    "b": {
                    "dst_path": "",
                    "keys": {}
                    }
                }
                },
                "c": {
                "dst_path": "",
                "keys": {
                    "d": {
                    "dst_path": "/home/user/Pictures/Photos",
                    "keys": {}
                    }
                }
                }
            }
            }

        actualOutput = sm.shortcutTree
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), True)

    def test_moveShortcutSequence_simple2(self):
        sm = ShortcutManager(self.window)
        sm.shortcutTree = {
            "keys": {
                "a": {
                "dst_path": "",
                "keys": {
                    "b": {
                    "dst_path": "",
                    "keys": {
                        "c": {
                        "dst_path": "",
                        "keys": {}
                        }
                    }
                    }
                }
                },
                "d": {
                "dst_path": "/home/user/Pictures/Photos",
                "keys": {}
                }
            }
            }

        expectedOutput = {
            "keys": {
                "a": {
                "dst_path": "",
                "keys": {
                    "b": {
                    "dst_path": "",
                    "keys": {
                        "c": {
                        "dst_path": "",
                        "keys": {
                            "d": {
                            "dst_path": "/home/user/Pictures/Photos",
                            "keys": {}
                            }
                        }
                        }
                    }
                    }
                }
                }
            }
            }

        sm.moveShortcutSequence("d>abc")

        actualOutput = sm.shortcutTree
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), True)


    def test_moveShortcutSequence_nonexisting_src(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag


        expectedTreeState = {
            "keys": {
                "a": {
                "dst_path": "",
                "keys": {
                    "b": {
                    "dst_path": "",
                    "keys": {
                        "c": {
                        "dst_path": "",
                        "keys": {
                            "d": {
                            "dst_path": "/home/user/Pictures/Photos",
                            "keys": {}
                            }
                        }
                        }
                    }
                    }
                }
                }
            }
            }

        actualOutput = sm.moveShortcutSequence("xyz>abc")
        expectedOutput = False

        actualTreeState = sm.shortcutTree
        self.assertEqual(actualTreeState, expectedTreeState)
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    def test_moveShortcutSequence_nonexisting_dst(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag


        expectedTreeState = {
            "keys": {
                "a": {
                "dst_path": "",
                "keys": {
                    "b": {
                    "dst_path": "",
                    "keys": {
                        "c": {
                        "dst_path": "",
                        "keys": {
                            "d": {
                            "dst_path": "/home/user/Pictures/Photos",
                            "keys": {}
                            }
                        }
                        }
                    }
                    }
                }
                }
            }
            }

        actualOutput = sm.moveShortcutSequence("abcd>xy")
        expectedOutput = False

        actualTreeState = sm.shortcutTree
        self.assertEqual(actualTreeState, expectedTreeState)
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    def test_moveShortcutSequence_empty_src(self):
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.setDataUnmodified()  # reset modified flag
        expectedTreeState = {
            "keys": {
                "a": {
                "dst_path": "",
                "keys": {
                    "b": {
                    "dst_path": "",
                    "keys": {
                        "c": {
                        "dst_path": "",
                        "keys": {
                            "d": {
                            "dst_path": "/home/user/Pictures/Photos",
                            "keys": {}
                            }
                        }
                        }
                    }
                    }
                }
                }
            }
            }

        actualOutput = sm.moveShortcutSequence(">abcd")
        expectedOutput = False

        actualTreeState = sm.shortcutTree
        self.assertEqual(actualTreeState, expectedTreeState)
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)        # sm.addShortcut('a')



    def test_moveShortcutSequence_dst_already_exist(self):
        # dst already exists in the target directory
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.addShortcutSequence("d")
        sm.updateDstPathForShortcut("d", "/home/user/Documents")
        sm.setDataUnmodified()  # reset modified flag

        expectedTreeState = {
            "keys": {
                "a": {
                "dst_path": "",
                "keys": {
                    "b": {
                    "dst_path": "",
                    "keys": {
                        "c": {
                        "dst_path": "",
                        "keys": {
                            "d": {
                            "dst_path": "/home/user/Pictures/Photos",
                            "keys": {}
                            }
                        }
                        }
                    }
                    }
                }
                },
                "d": {
                "dst_path": "/home/user/Documents",
                "keys": {}
                }
            }
            }


        actualOutput = sm.moveShortcutSequence("abcd>")  # d from abc should be moved to Level 1, but where alredy 'd' exists.
        expectedOutput = False

        actualTreeState = sm.shortcutTree
        self.assertEqual(actualTreeState, expectedTreeState)
        self.assertEqual(actualOutput, expectedOutput)
        self.assertEqual(sm.areShortcutsModified(), False)


    def test_moveShortcutSequence_comprehensive(self):
        # dst already exists in the target directory
        sm = ShortcutManager(self.window)
        sm.addShortcutSequence("abcd")
        sm.updateDstPathForShortcut("abcd", "/home/user/Pictures/Photos")
        sm.addShortcutSequence("d")
        sm.updateDstPathForShortcut("d", "/home/user/Documents")
        sm.setDataUnmodified()  # reset modified flag

        self.assertEqual(sm.moveShortcutSequence("abcd>"), False)
        self.assertEqual(sm.moveShortcutSequence(">bcde"), False)
        self.assertEqual(sm.moveShortcutSequence("#>?"), False)
        self.assertEqual(sm.moveShortcutSequence("ab#s>?"), False)
        self.assertEqual(sm.moveShortcutSequence("a<><p"), False)
        self.assertEqual(sm.moveShortcutSequence("ab>c/d"), False)


    # ========== getLastKey ==========
    def test_getLastKey(self):
        pass


    # ========== getLastKeyOfSequenceAndUpdate ==========
    def testaddShortcutSequence(self):
        pass

    # ========== getLastPossibleKeyOfSequence ==========
    def test_getLastPossibleKeyOfSequence(self):
        pass


    def tearDown(self):
        self.window.close()

if __name__ == '__main__':
    unittest.main()
