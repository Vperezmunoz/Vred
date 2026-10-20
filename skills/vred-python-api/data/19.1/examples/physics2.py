# Physics collision example with contact information
# source: physics2.html

# Find objects for Collision and Interpolators
  sphere = vrNodeService.findNode('Sphere')
  axis = vrNodeService.findNode('Axis')
  shape = vrNodeService.findNode('Cylinder')
  trans = vrNodeService.findNode('Trans')
  calcVertexNormals()

  # Set up the rotation of the sphere around the axis
  rotInt = vrInterpolator()
  rotSlide = vrRotationAxisSlide(sphere, axis, 0, 360, 6.0)
  rotInt.add(rotSlide)
  rotInt.setActive(True)

  # Set up the movement of the cylinder
  cylTrans = vrInterpolator()
  cylSlideUp = vrTranslationSlide(trans, 0,0,25, 0,0,500, 3.0)
  cylSlideDn = vrTranslationSlide(trans, 0,0,500, 0,0,25, 3.0)
  cylTrans.add(cylSlideUp)
  cylTrans.add(cylSlideDn)
  cylTrans.setActive(True)

  # Switch on physics to activate the collision detection pipeline
  vrPhysicsService.setActive(True)

  # Create convex hulls as collision shapes for the sphere and the cylinder.
  # We set 'merge geometries' to False, so that we get a separate convex hull
  # for each child node instead of a single convex hull for the entire node.
  hullConfig = vrdPhysicsHullConfig()
  hullConfig.setMergeGeometries(False)

  # Add the two nodes as kinematic objects so that we can move them in the scene
  vrPhysicsService.addKinematicObject(sphere, hullConfig)
  vrPhysicsService.addKinematicObject(shape, hullConfig)


  # Fetch the annotation node to display the collision point info
  note = vrAnnotationService.findAnnotation('CollisionPoint')

  # Helper function to get the correct colliding child node of the sphere.
  # The order of the colliding nodes is not guaranteed, so we have to check which
  # of the two nodes is the sphere's child.
  # The collision system always returns pairs, we look here for the
  # sphere's children. We know they are named 'Tri' followed by a number, so we can
  # use this to identify the correct child node.
  # The sphere node is merged into slices where every slice has the same color.
  #
  # Note: we have to use getCollidingNode1() to get the colliding child node
  # since we disabled 'merge geometries' on the convex hull config and
  # therefore have a hull for each child.
  # Using getCollidingRootNode1() would return the sphere, the node we had actually
  # registered for collision.
  def get_sphere_collision_node(nodeInfo):
      if nodeInfo.getCollidingNode1().getName().startswith("Tri"):
          return nodeInfo.getCollidingNode1()
      else:
          return nodeInfo.getCollidingNode2()

  # This is the function we call when a collision happens.
  # It fetches the sphere's colliding child node and applies it's
  # diffuse color to the cylinder and the annotation node.
  # Additonally we fetch the contact points from the collision
  # and position the annotation to the first reported contact point.
  # Since we already know that a collision has happened, there
  # has to be at least one contact.
  def update_collision(nodeInfo):
      vrAnnotationService.setShowAnnotations(True)
      collidingNode = get_sphere_collision_node(nodeInfo)
      mat = collidingNode.getMaterial()
      diffuse = mat.getDiffuseColor()

      vrMaterialService.applyMaterialToNodes(mat, [shape])
      backgroundColor = QColor();
      backgroundColor.setRgbF(diffuse.x(), diffuse.y(), diffuse.z())
      note.setLineColor(backgroundColor)
      note.setFontColor(backgroundColor)
      point = nodeInfo.getContactPoints()[0]
      numPoints = len(nodeInfo.getContactPoints())

      note.setPosition(point)
      note.setText(f'Contact points: {numPoints}\nFirst contact point:\nx {point.x():.2f}\ny {point.y():.2f}\nz {point.z():.2f}')


  # Register callbacks for the collisions. We also need to register to
  # 'continues' to always get updated contact points while the cylinder is
  # moving through the slices of the sphere.
  def collisionStart(nodeInfo):
      update_collision(nodeInfo)

  def collisionStopped(nodeInfo):
      vrAnnotationService.setShowAnnotations(False)

  def collisionContinues(nodeInfo):
      update_collision(nodeInfo)

  # Always make sure that the signals are not already connected when registering
  # them here as part of a variant. If they are not disconnected, the callbacks
  # would be registered again every time the variant is activated leading to
  # multiple activations of the callback functions.
  try:
      vrPhysicsService.collisionStarted.disconnect(start)
      vrPhysicsService.collisionStarted.disconnect(stop)
      vrPhysicsService.collisionStarted.disconnect(cont)
  except:
      pass

  start = vrPhysicsService.collisionStarted.connect(collisionStart)
  stop = vrPhysicsService.collisionStopped.connect(collisionStopped)
  cont = vrPhysicsService.collisionContinues.connect(collisionContinues)

  # Stop the rotation and movement
  rotInt.setActive(False)
  cylTrans.setActive(False)
