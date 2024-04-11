import cbpro


def main():

    public_client = cbpro.PublicClient()
    products = public_client.get_products()
    ids = {}
    for prod in products:
        if prod["status"] == "online" and prod["trading_disabled"] is False:

            start = prod['id'].find("-")
            first_token =  prod["id"][:start]
            second_token = prod["id"][start+1:]
            if first_token in ids:
                ids[first_token].add(second_token)
            else:
                ids[first_token] = set()
                ids[first_token].add(second_token)

            if second_token in ids:
                ids[second_token].add(first_token)
            else:
                ids[second_token] = set()
                ids[second_token].add(first_token)

    for id in ids:
        print(id, ids[id])

if __name__ == "__main__":
    main()