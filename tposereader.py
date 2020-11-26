import os
import c4d
import math

#----begin_resource_section----
from bootstrap4c4d import Description, Assignment, Group, Container

crumb_flag_group_open = Assignment("DEFAULT", 1)

settings_draw_debug_lines = Description({
    "id": "SETTINGS_DRAW_DEBUG_LINES",
    "key": "BOOL",
    "value": [
        Assignment("ANIM", "OFF")
    ],
    "locales": {
        "strings_us": "Draw Debug Lines"
    }
})

settings_origin_object = Description({
    "id": "SETTINGS_ORIGIN_OBJECT",
    "key": "LINK",
    "value": [
        Assignment("ANIM", "OFF"),
        Description({
            "key": "ACCEPT", 
            "value": [
                Assignment("Obase", None)
            ]
        })
    ],
    "locales": {
        "strings_us": "Origin"
    }
})

settings_target_object = Description({
    "id": "SETTINGS_TARGET_OBJECT",
    "key": "LINK",
    "value": [
        Assignment("ANIM", "OFF"),
        Description({
            "key": "ACCEPT", 
            "value": [
                Assignment("Obase", None)
            ]
        })
    ],
    "locales": {
        "strings_us": "Target"
    }
})

axis_x = Assignment(None, None, {
    "id": "AXIS_X",
    "locales": {
        "strings_us": "X"
    }
})

axis_y = Assignment(None, None, {
    "id": "AXIS_Y",
    "locales": {
        "strings_us": "Y"
    }
})

axis_z = Assignment(None, None, {
    "id": "AXIS_Z",
    "locales": {
        "strings_us": "Z"
    }
})

settings_axis = Description({
    "id": "SETTINGS_AXIS",
    "key": "LONG",
    "value": [
        Assignment("ANIM", "OFF"),
        Assignment("CYCLE", [
            axis_x,
            axis_y,
            axis_z
        ])
    ],
    "locales": {
        "strings_us": "Read Axis"
    }
})

result_rotation = Description({
    "id": "RESULT_ROTATION",
    "key": "REAL",
    "value": [
        Assignment("ANIM", "OFF"),
        Assignment("UNIT", "DEGREE")
    ],
    "locales": {
        "strings_us": "Rotation"
    }
})

group_settings = Group("GROUP_SETTINGS", {
    "value": [
        crumb_flag_group_open,
        settings_draw_debug_lines,
        settings_origin_object,
        settings_target_object,
        settings_axis
    ],
    "locales": {
        "strings_us": "Settings"
    }
})

group_result = Group("GROUP_RESULT", {
    "value": [
        crumb_flag_group_open,
        result_rotation
    ],
    "locales": {
        "strings_us": "Result"
    }
})

root = Container("Tposereader", {
    "value": [
        Assignment("NAME", "Tposereader"),
        Assignment("INCLUDE", "Tbase"),
        Assignment("INCLUDE", "Texpression"),
        group_settings,
        group_result
    ],
    "locales": {
        "strings_us": "PoseReader"
    }
})

#----end_resource_section----

#----begin_id_section----
SETTINGS_DRAW_DEBUG_LINES = settings_draw_debug_lines.GetId()
SETTINGS_ORIGIN_OBJECT = settings_origin_object.GetId()
SETTINGS_TARGET_OBJECT = settings_target_object.GetId()
SETTINGS_AXIS = settings_axis.GetId()
SETTINGS_AXIS_X = axis_x.GetId()
SETTINGS_AXIS_Y = axis_y.GetId()
SETTINGS_AXIS_Z = axis_z.GetId()

RESULT_ROTATION = result_rotation.GetId()
#----end_id_section----

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 123456789


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
        targetMatrix = targetObject.GetMg()
        targetRotationMatrix = c4d.Matrix(
            c4d.Vector(0, 0, 0),
            targetMatrix.v1,
            targetMatrix.v2,
            targetMatrix.v3
        )

        originMatrix = originObject.GetMg()
        originRotationMatrix = c4d.Matrix(
            c4d.Vector(0, 0, 0),
            originMatrix.v1,
            originMatrix.v2,
            originMatrix.v3
        )

        offsetMatrix = (~originRotationMatrix) * targetRotationMatrix

        return offsetMatrix.MulV(offset.GetNormalized())

        # return c4d.Vector(targetPosition - originObject.GetMg().off).GetNormalized()
    
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

        originObject = data[SETTINGS_ORIGIN_OBJECT]
        targetObject = data[SETTINGS_TARGET_OBJECT]
        axis = data[SETTINGS_AXIS]

        if originObject and targetObject:
            try:
                if axis == SETTINGS_AXIS_X:
                    # calculate rotation along x
                    targetVectorX = PoseReader.CalculateVector(originObject, targetObject, c4d.Vector(0, 0, 100.0))

                    self.rotation = CalculateRotation(targetVectorX.z, targetVectorX.y)
                elif axis == SETTINGS_AXIS_Y:
                    # calculate rotation along y
                    targetVectorY = PoseReader.CalculateVector(originObject, targetObject, c4d.Vector(100.0, 0, 0))

                    self.rotation = CalculateRotation(targetVectorY.x, targetVectorY.z)
                elif axis == SETTINGS_AXIS_Z:
                    # calculate rotation along z
                    targetVectorZ = PoseReader.CalculateVector(originObject, targetObject, c4d.Vector(0, 100.0, 0))

                    self.rotation = CalculateRotation(targetVectorZ.y, targetVectorZ.x)
            except ZeroDivisionError:
                pass

        data[RESULT_ROTATION] = self.rotation
        
        return c4d.EXECUTIONRESULT_OK

    def Draw(self, tag, op, bd, bh):
        data = tag.GetDataInstance()
        drawpass = bd.GetDrawPass()

        if data[SETTINGS_DRAW_DEBUG_LINES]:
            originObject = data[SETTINGS_ORIGIN_OBJECT]
            axis = data[SETTINGS_AXIS]

            originMatrix = originObject.GetMg()

            position = originMatrix.off

            if axis == SETTINGS_AXIS_X:
                # aim axis side
                up = c4d.Vector(0, 1.0, 0)
                aim = c4d.Vector(1.0, 0, 0)
                side = c4d.Vector(0, 0, 1.0)
            elif axis == SETTINGS_AXIS_Y:
                # aim axis up
                up = c4d.Vector(0, 0, -1.0)
                aim = c4d.Vector(0, 1.0, 0)
                side = c4d.Vector(1.0, 0, 0)
            elif axis == SETTINGS_AXIS_Z:
                # aim axis forward
                up = c4d.Vector(0, 1.0, 0)
                aim = c4d.Vector(0, 0, 1.0)
                side = c4d.Vector(1.0, 0, 0)

            debugMatrix = c4d.Matrix(
                position,
                originMatrix.MulV(side),
                originMatrix.MulV(up),
                originMatrix.MulV(aim)
            )

            # debugMatrix = debugMatrix * originMatrix

            scale = 10.0

            baseLineTargetPosition = (side * scale) * originMatrix
            bd.SetPen(c4d.GetViewColor(c4d.VIEWCOLOR_ZAXIS))
            bd.DrawLine(position, baseLineTargetPosition, 0)

            rotation = c4d.Quaternion()
            rotation.SetAxis(aim, self.rotation)
            rotationMatrix = rotation.GetMatrix()

            rotationLineTargetPosition = (rotationMatrix.MulV(side) * scale) * originMatrix
            bd.SetPen(c4d.GetViewColor(c4d.VIEWCOLOR_YAXIS))
            bd.DrawLine(position, rotationLineTargetPosition, 0)

            # draw circle
            debugMatrix.Scale(scale)

            bd.SetPen(c4d.GetViewColor(c4d.VIEWCOLOR_XAXIS))
            bd.DrawCircle(debugMatrix)    

        return True

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
    fn = os.path.join(directory, "res", "tposereader.png")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    c4d.plugins.RegisterTagPlugin(id=PLUGIN_ID,
        str="PoseReader",
        info=c4d.TAG_EXPRESSION | c4d.TAG_VISIBLE | c4d.TAG_IMPLEMENTS_DRAW_FUNCTION,
        g=PoseReader,
        description="Tposereader",
        icon=bmp
    )