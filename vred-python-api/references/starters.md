# Verified starting points

Every call below was taken from the index of the installed VRED build, not from memory.
Anything not listed here: look it up (`py vredapi.py find …`) rather than guessing.

## Scene graph

```python
root = vrScenegraphService.getRootNode()
node = vrNodeService.findNode("Door_L")                       # exact name
nodes = vrNodeService.findNodes("Eye_*", wildcard=True)       # wildcard
node = vrNodeService.findNodeWithPath("/Root/Body/Door_L")
selected = vrScenegraphService.getSelectedNodes()             # List[vrdNode]
group = vrScenegraphService.groupNodes(nodes)                 # new group holding them
children = node.getChildren()

if node.isValid():          # isValid() is inherited from vrdSceneObject
    node.setVisibilityFlag(False)
    node.setName("Door_Left")
```

`vrdNode` is a handle — after a scene reload it goes stale, so re-find rather than cache.
Transform-specific calls live on `vrdTransformNode` (`getLocalTranslation()`,
`addLocalTranslation(delta)`, …); get there with the node's transform accessors.

## Materials

```python
mat = vrMaterialService.findMaterial("plasticmat")
if not mat.isValid():
    mat = vrMaterialService.createMaterial("plasticmat", vrMaterialTypes.MaterialType.Plastic)
vrMaterialService.applyMaterialToNodes(mat, nodes)
```

Enum spelling matters — `py vredapi.py enum MaterialType`.

## Files

```python
vrFileIOService.loadFile(r"C:\data\car.vpb")
job = vrFileIOService.exportNodes(r"C:\out\body.fbx", nodes)
```

Import and export are asynchronous jobs; connect to the service's completion signals
(`py vredapi.py class vrFileIOService`) rather than assuming the file exists on the next line.

## Web engines (HTML / video on a texture)

```python
engine = vrWebEngineService.getWebEngine("Player")
if not engine.isValid():
    engine = vrWebEngineService.createWebEngine("Player")
```

For the whole working pattern — texture slots, autoplay, codecs — use the
`vred-script-plugin` skill; those behaviours contradict the reference docs.

## Legacy v1 still seen in customer scripts

```python
vrFileIO.load("car.vpb")          # v1 module function
findNode("Door_L")                 # v1 global, injected in the VRED terminal
```

Read it, don't write it. Look up any v1 call with `py vredapi.py find <name> --api v1`.
