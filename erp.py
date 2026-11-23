"""Transactional inventory ERP reference; SQLite, no third-party dependencies."""
import argparse,json,sqlite3
from pathlib import Path

def connect(path):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(p)
    c.execute('PRAGMA foreign_keys=ON')
    c.executescript("""
        CREATE TABLE IF NOT EXISTS item(sku TEXT PRIMARY KEY,name TEXT NOT NULL,available INTEGER NOT NULL DEFAULT 0 CHECK(available>=0));
        CREATE TABLE IF NOT EXISTS sales_order(order_id TEXT PRIMARY KEY,customer TEXT NOT NULL,sku TEXT NOT NULL REFERENCES item(sku),quantity INTEGER NOT NULL CHECK(quantity>0),unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents>=0));
        CREATE TABLE IF NOT EXISTS movement(reference_code TEXT PRIMARY KEY,sku TEXT NOT NULL REFERENCES item(sku),delta INTEGER NOT NULL,kind TEXT NOT NULL);
    """)
    return c

def product(c,sku,name):
    if not sku or not name:raise ValueError('SKU and name required')
    with c:c.execute('INSERT INTO item(sku,name) VALUES (?,?)',(sku,name))

def receipt(c,reference,sku,quantity):
    if type(quantity) is not int or quantity<1:raise ValueError('Positive integer quantity required')
    with c:
        c.execute('INSERT INTO movement VALUES (?,?,?,?)',(reference,sku,quantity,'receipt'))
        c.execute('UPDATE item SET available=available+? WHERE sku=?',(quantity,sku))
        if c.execute('SELECT changes()').fetchone()[0]==0:raise KeyError(sku)

def sale(c,order_id,customer,sku,quantity,unit_price_cents):
    if type(quantity) is not int or quantity<1 or type(unit_price_cents) is not int or unit_price_cents<0:raise ValueError('Invalid quantity or price')
    if not order_id or not customer:raise ValueError('Order and customer required')
    with c:
        row=c.execute('SELECT available FROM item WHERE sku=?',(sku,)).fetchone()
        if row is None:raise KeyError(sku)
        if row[0]<quantity:raise ValueError('Insufficient stock')
        c.execute('INSERT INTO sales_order VALUES (?,?,?,?,?)',(order_id,customer,sku,quantity,unit_price_cents))
        c.execute('INSERT INTO movement VALUES (?,?,?,?)',('SO:'+order_id,sku,-quantity,'sale'))
        c.execute('UPDATE item SET available=available-? WHERE sku=?',(quantity,sku))

def state(c):
    return {'items':[dict(zip(('sku','name','available'),row)) for row in c.execute('SELECT sku,name,available FROM item ORDER BY sku')],
            'orders':[dict(zip(('order_id','customer','sku','quantity','unit_price_cents'),row)) for row in c.execute('SELECT * FROM sales_order ORDER BY order_id')],
            'movements':[dict(zip(('reference_code','sku','delta','kind'),row)) for row in c.execute('SELECT * FROM movement ORDER BY reference_code')]}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--db',default='out/erp.sqlite3')
    sub=parser.add_subparsers(dest='command',required=True)
    a=sub.add_parser('product');a.add_argument('sku');a.add_argument('name')
    a=sub.add_parser('receipt');a.add_argument('ref');a.add_argument('sku');a.add_argument('quantity',type=int)
    a=sub.add_parser('sale');a.add_argument('order_id');a.add_argument('customer');a.add_argument('sku');a.add_argument('quantity',type=int);a.add_argument('unit_price_cents',type=int)
    sub.add_parser('report');args=parser.parse_args()
    with connect(args.db) as c:
        if args.command=='product':product(c,args.sku,args.name)
        elif args.command=='receipt':receipt(c,args.ref,args.sku,args.quantity)
        elif args.command=='sale':sale(c,args.order_id,args.customer,args.sku,args.quantity,args.unit_price_cents)
        print(json.dumps(state(c),indent=2))
if __name__=='__main__':main()
