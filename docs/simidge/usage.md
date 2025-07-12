# SiMidge

## Main Search

### Filters

- Type: type of resource to search for (eg. BHAV, BCON, etc.)
- Instance: instance of resource to search for
- Name: string to search for within the name of a resource
- Target: string (for STR#, CTSS, and TTAs resources) or bytes (for binary resources) to search for within the contents of the resource

### Search Type

- Objects: search within objects.package
- Downloads: search within your downloads folder
- Other File(s): provides a file picker dialog to select files to search in
- Other Folder: provides a file picker dialog to select a directory to search in

## Find

### Conflicts

#### All

Searches for all conflicts within your downloads folder.

#### With File

Searches your downloads folder for conflicts with a selected file.

#### In Folder

Searches a selected folder for conflicts.

### Duplicate Meshes

Searches your downloads folder for duplicate GMDC (3d mesh) resources.

### Translated/Empty Strings

Searches string (STR#, CTSS, and TTAs) resources for any that have translations, are completely empty, have descriptions, or can otherwise be cleaned by SimPE. Skips lua STR#s (since they may define scripts in the description).

## Compare

#### Packages (changed)

Compare the selected packages for resources that are shared and differ between them.

#### Packages (unchanged)

Compare the selected packages for resources that are shared between them with no differences.

#### Packages (added/removed)

Compare the selected packages for resources that only exist in one of the packages.

#### Resources

Check if an extracted resource is identical to the version in objects.package.
