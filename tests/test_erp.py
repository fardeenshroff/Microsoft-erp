import sqlite3
import pytest
from erp import connect,product,receipt,sale,state

def test_receiving_sale_and_stock_reconciliation(tmp_path):
    with connect(tmp_path/'erp.db') as c:
        product(c,'SENSOR','Proximity sensor')
        receipt(c,'PO-001','SENSOR',10)
        sale(c,'SO-001','Ada','SENSOR',3,12500)
        result=state(c)
        assert result['items'][0]['available']==7
        assert sum(x['delta'] for x in result['movements'])==7
        assert result['orders'][0]['unit_price_cents']==12500

def test_errors_do_not_mutate_stock(tmp_path):
    with connect(tmp_path/'erp.db') as c:
        product(c,'HMI','Display');receipt(c,'GRN-001','HMI',3)
        with pytest.raises(ValueError):sale(c,'X','Sam','HMI',4,10000)
        with pytest.raises(sqlite3.IntegrityError):receipt(c,'GRN-001','HMI',1)
        sale(c,'O1','Sam','HMI',2,10000)
        with pytest.raises(sqlite3.IntegrityError):sale(c,'O1','Sam','HMI',1,10000)
        assert state(c)['items'][0]['available']==1
