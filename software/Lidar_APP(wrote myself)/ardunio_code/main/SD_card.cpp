#include "SD.h"
#include "SD_card.h"
void SD_module_init(int CS_port)
{
    SD.begin(CS_port);
    if(!SD.exists("Database"))
    {
        SD.mkdir("Database");
    }
}