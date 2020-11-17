CONTAINER Tposereader
{
    NAME Tposereader;
    INCLUDE Tbase;
    INCLUDE Texpression;

    GROUP SETTINGS_GROUP
    {
        DEFAULT 1;

        LINK ORIGIN_OBJECT 
        {
            ANIM OFF;
            ACCEPT 
            {
                Obase;
            }
        }

        LINK TARGET_OBJECT 
        {
            ANIM OFF;
            ACCEPT 
            {
                Obase;
            }
        }

        LONG SETTINGS_AXIS
        {
            ANIM OFF;
            CYCLE
            {
                SETTINGS_AXIS_X;
                SETTINGS_AXIS_Y;
                SETTINGS_AXIS_Z;
            }
        } 
    }

    GROUP RESULT_GROUP
    {
        REAL RESULT_ROTATION 
        {
            ANIM OFF;
            UNIT DEGREE;
        }        
    }
}
