# learned

- Replacing data value with Object
    - filename replaced for object containing filename and path.
    - Changes in object are available everywhere, where the object is currently stored or referenced.
    - No need to change a string (filename during rename...) on many places.
    - Don's use primitives much
        - https://refactoring.guru/smells/primitive-obsession

- Command pattern

- Short methods's parameter list

- Independent classes (e.g. CropService...)
    - Working even as a standalone
    - -> Decoupled from the app
    - Generally: dont implement unrelated functionality in the classes

- Chain of Responsibility
    - Passing a message through UI elements (button->ImagePreview->GalleryManager->...)

- Indirect access to fields (getters / setters)
    - Flexibility

- Eliminate Message Chains

- Prevent Shotgun Surgery
    - Making any modifications requires that you make many small changes to many different classes.

- Replace nested conditions with guard clauses

- Composition root
