# Wallapop update notifier

### This package can be used to provide updates when new products appear on Wallapop. Install it just by using:<br><br>
`pip install wallapopUpdateWatcher`
### Basic usage example
```python
from wallapopUpdateWatcher import updateWatcher,Query,Producto
import asyncio
async def callback(q: Query, l: list[Producto]):
    for prod in l:
        print(prod.msg())


async def main():
    watcher = updateWatcher(callback)
    await watcher.create("Iphone",strategy="price", min_max_sale_price = (15,30))
    # this creates a search for the product "Iphone"
    # between 15€ and 30€. 

    while True:
        await watcher.checkOperation()
        await asyncio.sleep(5)

asyncio.run(main())
```

## Strategies:
Strategies are what decides if a product that has already appeared sometime is going to be notified. There are 3 strategies:
- Price:
This strategy only adds the product if its price has changed. It is the **default** strategy.

- New:
This strategy only notifies new products.

- Any:
This strategy notifies any product, even if it has already been notified.