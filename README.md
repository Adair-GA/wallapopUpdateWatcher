# Wallapop update notifier

### This package can be use to provide updates when new products appear on Wallapop. Install it just by using:<br><br>
`pip install wallapopUpdateWatcher`
### Basic usage example
```python
from wallapopUpdateWatcher import updateWatcher,Query,Producto
import asyncio
async def callback(q: Query, l: list[Producto])
    for prod in producto:
        print(q.msg())


async def main()
    watcher = wallapopUpdateWatcher(callback)
    await watcher.create("Keywords",(15,30))
    # this creates a search for the product "Keywords"
    # between 15€ and 30€. 

    while(True):
        await watcher.checkOperation()
        await asyncio.sleep(5)

asyncio.run(main())
```
