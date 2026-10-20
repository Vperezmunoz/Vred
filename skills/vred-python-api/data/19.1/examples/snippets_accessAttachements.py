# accessAttachments
# source: accessAttachements.html

# © 2026 Autodesk, Inc. All rights reserved.

# example for handling attachments

# create a name attachment
nameAttachment = createAttachment("Name")
# set the name value of the attachment
vrFieldAccess(nameAttachment).setString('name', "MyAttachmentNodeName")
# get the selected node and add the attachment.If a name attachment is already present, it will be replaced
node = getSelectedNode()
node.addAttachment(nameAttachment)
# check if the attachment exists and print the name
if node.hasAttachment('Name'):
    attachment = node.getAttachment('Name')
    print(vrFieldAccess(attachment).getString('name'))

# access core attachments
if node.fields().hasField('material'):
    mat = vrFieldAccess(node.fields().getFieldContainer("material"))
    if mat.hasAttachment('Name'):
        matNameAttachment = mat.getAttachment('Name')
        print(vrFieldAccess(matNameAttachment).getString('name'))


# delete a touch sensor attachment
if node.hasAttachment("TouchSensorAttachment"):
    att = node.getAttachment("TouchSensorAttachment")
    node.subAttachment(att)
