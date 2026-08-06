# Physics basic collision example
# source: physics.html

# This example shows how to use the Physics collision pipeline.
  # We add a few nodes as kinematic actors, so that we can move them
  # in the scene and react on collisions between them.
  #
  # The only reaction on collision is that we render the colliding nodes
  # with an override material to highlight it. Each registered node has
  # a different highlight material assigned in the highlight function.

  # The 'speedshape' node is animated. If the animation is played, the node
  # will be moved from side to side and collide with the other nodes.


  # First fetch some nodes from the scene graph that
  # should get a collision object

  teddy = vrNodeService.findNode("Teddy_Bear")
  teddy2 = vrNodeService.findNode("Teddy_Bear2")
  speedshape = vrNodeService.findNode("Speedshape")
  cloth = vrNodeService.findNode("Cloth_Example")
  logo = vrNodeService.findNode("VRED_Logo")

  # The next step is creating collision shapes for the nodes we have collected.
  # We use objects called 'configurations' to define how the collision shape should
  # look like. Configurations are a collection of parameters that influence the way
  # the collision shape is created.

  # Now we prepare the physics configurations for the nodes. The configuration
  # determines what kind of collision shape is built for the node.
  # Since it's not possible to have moving triangle meshes in the physics simulation,
  # we have to approximate the geometry of the nodes with simpler shapes. We use
  # a technique called 'convex decomposition' to split the geometry into multiple
  # smaller convex hulls. This is a good compromise between accuracy and performance.
  convexDecompConf = vrdPhysicsConvexConfig()

  # After the configuration is created, we can change its properties to fine tune
  # the collision shape creation. In this case we increase the maximum number of
  # convex hulls the algorithm is allowed to create from the default 64 to 256 to give
  # it more freedom to approximate the geometry.
  convexDecompConf.setMaxNumberOfConvexHulls(256)

  # This is the standard configuration for a convex hull.
  convexHullConf = vrdPhysicsHullConfig()

  # Here we have a special case of convex hull. If the bounding box option is set,
  # we create a convex hull for the bounding box of the object. This is extremely fast and
  # results in an object aligned bounding box collision shape.
  boxConf = vrdPhysicsHullConfig()
  boxConf.setUseBoundingBox(True)

  # Add the nodes to the service along with their configurations.
  vrPhysicsService.addKinematicObject(teddy, convexDecompConf)
  vrPhysicsService.addKinematicObject(speedshape, convexHullConf)
  vrPhysicsService.addKinematicObject(cloth, convexDecompConf)
  vrPhysicsService.addKinematicObject(logo, convexDecompConf)
  vrPhysicsService.addKinematicObject(teddy2, boxConf)

  # The service needs to be set to 'active' to start the collision pipeline.
  vrPhysicsService.setActive(True)

  # Here we try to connect to the NVidia debugger in case it's already running.
  vrPhysicsService.connectDebugger()


  # A bit of cleanup when new scene is executed.
  def newSceneCallback():
      vrPhysicsService.collisionStarted.disconnect()
      vrPhysicsService.collisionStopped.disconnect()
      vrPhysicsService.collisionContinues.disconnect()

  setNewSceneCB(newSceneCallback)

  # This map is used for some bookkeeping of the highlight state of the nodes.
  # It uses reference counting to track the number of collisions a node is involved in.
  # This is to avoid flickering if a collision with one object ends while a collision
  # with another object is still ongoing. In this case the highlight function is called
  # twice, once with 'True' (continues) and once with 'False' (stopped).
  collisionState = {teddy:0, speedshape:0, cloth:0, logo:0, teddy2:0}

  def highlight(node, enable):
      # prevents removing highlighting when node collides with
      # multiple nodes and one of the collisions ends
      if not enable and collisionState[node] > 0:
          return

      # here we select a different material to highlight
      # each node when it collides
      if node.getName() == "Teddy_Bear":
          material = "collision2"
      elif node.getName() == "Teddy_Bear2":
          material = "collision3"
      elif node.getName() == "Cloth_Example":
          material = "collision4"
      elif node.getName() == "VRED_Logo":
          material = "collision5"
      else:
          material = "collision1"

      # to highlight the node, we use the override material feature
      setNodeVisibilityFlags(node,
          True,True,True,True,True,True,
          True,True,True,True,enable,material)


  # Here we register three callback functions and connect them
  # to the started / stopped / continues signals of the service.

  def collisionStart(nodeInfo):
      # show the contactpoints (careful, printing the points causes
      # a major slowdown)
      #contactpoints = nodeInfo.getContactPoints()
      #if len(contactpoints) > 0:
      #    for num, contact in enumerate(contactpoints):
      #        print("contact ({}): {} {} {}".format(num, contact.x(),
      #            contact.y(), contact.z()))

      # We increment the counter for the highlighting when
      # a new collision event starts
      collisionState[nodeInfo.getCollidingRootNode1()] +=1
      collisionState[nodeInfo.getCollidingRootNode2()] +=1

      # Turn on the highlighting for both nodes
      highlight(nodeInfo.getCollidingRootNode1(), True)
      highlight(nodeInfo.getCollidingRootNode2(), True)

  def collisionStopped(nodeInfo):
      # Decrement the refcount for the highlighting
      # when a collision between two objects ends.
      collisionState[nodeInfo.getCollidingRootNode1()] -=1
      collisionState[nodeInfo.getCollidingRootNode2()] -=1

      # Also remove the highlighting.
      highlight(nodeInfo.getCollidingRootNode1(), False)
      highlight(nodeInfo.getCollidingRootNode2(), False)

  def collisionContinues(nodeInfo):
      # While the collision is ongoing, we make sure that
      # the highlighting is still applied. (This is not strictly
      # necessary, but it's a good idea to make sure the highlighting is
      # still active and not overwritten).
      highlight(nodeInfo.getCollidingRootNode1(), True)
      highlight(nodeInfo.getCollidingRootNode2(), True)


  # Connect the callbacks to the service
  vrPhysicsService.collisionStarted.connect(collisionStart)
  vrPhysicsService.collisionStopped.connect(collisionStopped)
  vrPhysicsService.collisionContinues.connect(collisionContinues)
