import os
import c4d
import math

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 123456789

# IDs
ORIGIN_OBJECT = 2000
TARGET_OBJECT = 2001

SETTINGS_AXIS = 2002
SETTINGS_AXIS_X = 2003
SETTINGS_AXIS_Y = 2004
SETTINGS_AXIS_Z = 2005

RESULT_ROTATION = 3000

def CalculateRotation(x, y):
    return 2 * math.atan(y / (x + math.sqrt(math.pow(x, 2) + math.pow(y, 2))))

class PoseReader(c4d.plugins.TagData):
    """Look at Camera"""
    
    def Init(self, node):
        """
        Called when Cinema 4D Initialize the TagData (used to define, default values)
        :param node: The instance of the TagData.
        :type node: c4d.GeListNode
        :return: True on success, otherwise False.
        """

        data = node.GetDataInstance()

        data[SETTINGS_AXIS] = SETTINGS_AXIS_X

        self.rotation = 0.0
        self.axis = SETTINGS_AXIS_X

        c4d.EventAdd()

        return True

    @classmethod
    def CalculateVector(cls, originObject, targetObject, offset):
        targetPosition = offset * targetObject.GetMg() * ~originObject.GetMg()

        return c4d.Vector(targetPosition - originObject.GetMg().off).GetNormalized()
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        """
        Called by Cinema 4D at each Scene Execution, this is the place where calculation should take place.
        :param tag: The instance of the TagData.
        :type tag: c4d.BaseTag
        :param doc: The host document of the tag's object.
        :type doc: c4d.documents.BaseDocument
        :param op: The host object of the tag.
        :type op: c4d.BaseObject
        :param bt: The Thread that execute the this TagData.
        :type bt: c4d.threading.BaseThread
        :param priority: Information about the execution priority of this TagData.
        :type priority: EXECUTIONPRIORITY
        :param flags: Information about when this TagData is executed.
        :type flags: EXECUTIONFLAGS
        :return:
        """
        data = tag.GetDataInstance()

        originObject = data[ORIGIN_OBJECT]
        targetObject = data[TARGET_OBJECT]
        axis = data[SETTINGS_AXIS]

        if originObject and targetObject:
            try:
                if axis == SETTINGS_AXIS_X:
                    # calculate rotation along x
                    targetVectorX = PoseReader.CalculateVector(originObject, targetObject, c4d.Vector(0, 0, 100))

                    self.rotation = CalculateRotation(targetVectorX.z, targetVectorX.y)
                elif axis == SETTINGS_AXIS_Y:
                    # calculate rotation along y
                    targetVectorY = PoseReader.CalculateVector(originObject, targetObject, c4d.Vector(100, 0, 0))

                    self.rotation = CalculateRotation(targetVectorY.x, targetVectorY.z)
                elif axis == SETTINGS_AXIS_Z:
                    # calculate rotation along z
                    targetVectorZ = PoseReader.CalculateVector(originObject, targetObject, c4d.Vector(0, 100, 0))

                    self.rotation = math.radians(90.0) - CalculateRotation(targetVectorZ.x, targetVectorZ.y)
            except ZeroDivisionError:
                pass

        data[RESULT_ROTATION] = self.rotation
        
        return c4d.EXECUTIONRESULT_OK

    # def SetDParameter(self, node, id, t_data, flags):
    #     if not node:
    #         return

    #     data = node.GetDataInstance()

    #     print(id[0].id, SETTINGS_AXIS)
    #     if id[0].id == SETTINGS_AXIS:
    #         print(data[SETTINGS_AXIS])

    #     return False


if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "tposereader.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    c4d.plugins.RegisterTagPlugin(id=PLUGIN_ID,
        str="PoseReader",
        info=c4d.TAG_EXPRESSION | c4d.TAG_VISIBLE,
        g=PoseReader,
        description="Tposereader",
        icon=bmp
    )