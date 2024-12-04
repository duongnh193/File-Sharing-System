#ifndef INVENTORYITEM_H
#define INVENTORYITEM_H
#include <string>
class InventoryItem
{
public:
    InventoryItem();
    InventoryItem(std::string d, double c, int u);

    std::string getDescriptions() const;
    void setDescriptions(const std::string &newDescriptions);
    double getCost() const;
    void setCost(double newCost);
    int getUnits() const;
    void setUnits(int newUnits);

private:
    std::string descriptions;
    double cost;
    int units;
};

#endif // INVENTORYITEM_H
