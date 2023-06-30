# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import pytest

from classquiz.kahoot_importer.get import get


@pytest.mark.order(-2)
@pytest.mark.asyncio
async def test_get():
    await get("1f95eb0b-fcf4-4db2-879b-5418ef75116b")
    await get("c63d4d39-767e-4754-8c16-66c3c2d9633c")
    await get("c5d31de6-4598-4574-8e67-ca9a2aba49f8")
    await get("3d545fc3-b830-44b6-94ac-c8e4a3c9fb88")
    quiz_list = [
        "c63d4d39-767e-4754-8c16-66c3c2d9633c",
        "a73689d2-1108-4524-88e1-10c54282346c",
        "e8e2d869-7c75-4ad6-8872-031bc8e37fa9",
        "387b4139-9e77-4b47-93b7-dbb6d75c54d1",
        "a1fff657-b99d-4547-93cf-4e9629994844",
        "0880d792-a77e-4cba-8a8b-359de40ffe76",
        "e2d12f01-a3dd-4d0e-a6c4-29f38046117f",
        "e0af9b8e-8840-4a7d-8d51-3d02bb6a07e7",
        "e655c086-558d-4602-99fd-5fc429ffe0ce",
        "1642f29d-b5cb-4213-82e6-7c1fae401aca",
        "fabdd572-da3e-4621-b912-41b9bc5a18fb",
        "ded3cbbf-5af3-4761-a6da-b3b6ca040e1a",
        "370b3e33-ed97-4d36-9362-7f76aa9d12b9",
        "cfa32a28-1a01-47f1-9bca-c85640bceeb8",
        "993f615d-6890-4dd3-ac08-f462de9ac5a3",
        "7f08a377-e371-425e-95f9-7196401ae7ff",
        "19656fed-5891-48e7-ae7f-1358f623bfd0",
        "5e766d32-930a-4640-82a1-87c58612f579",
        "ab2450e8-ecbb-4aed-bb3c-87e47b2b81f5",
        "dd3c9175-addd-48df-8297-7598d4f12006",
        "b8de862c-fc4b-4df6-9fa5-81b91868fc3b",
        "3b082f4e-9c50-45ea-98c4-3845b14e400c",
        "10179f67-a344-4fd0-80a1-d1e1b6ca7953",
        "8288c1dd-9675-411c-9175-4180004da3c3",
        "af838c22-dcbb-497d-8c7b-f6499835b83d",
        "152c5fdb-3b0a-4cdf-a0d9-1984de0643ad",
        "846fd2bb-6b95-4333-b5d4-ef0a363e73a9",
        "dd6b446f-817b-469b-9e6b-e1d34c466a7f",
        "2720d636-8918-4c6a-86a9-928c489382f4",
        "a6985641-df97-4e56-97fc-e0901e32b464",
        "1d2705b4-b79e-4b51-8d61-cfb60fc7d1b9",
        "677fa485-4231-4479-beb2-fe757053bf41",
        "2b6379f8-450e-46c0-a854-5e368a03d5a6",
        "f3ba42fe-11e8-47fc-8978-8d67bc0ce0b1",
        "51d2e839-a9d7-4f26-b1fd-fb0743c3a236",
        "f2212243-4553-456d-87e7-7ddfd6ee7563",
        "2d6982d3-7b46-4022-bbb6-cb5451c581ba",
        "1cccae22-5140-46b5-ba6a-aa17cec14dc3",
        "b01dd2c2-ffcf-4c02-a274-e12296dbe4e1",
        "2669d193-a81f-4752-a003-dd2433beef92",
        "06203ee6-3615-4e26-bb08-4fab249698a4",
        "933c1426-c759-43a3-9770-c8e3948db998",
        "02046384-fb05-4f1d-855a-f0e52a0761e3",
        "b5266e9b-7372-4df0-94a9-ec8a6c0aabc6",
        "fb8e3a3d-505a-4157-bd9a-b73b00591f10",
        "42092675-9171-400f-ab4d-c898ec9f70bd",
        "1d6307e2-98c2-42f2-b765-d02a68e0da80",
        "8f431ed0-31df-4435-bcba-aff46929fe82",
        "d573d76f-d715-4a54-bdde-7ac7b6235fb2",
        "feb8985b-84fb-4d41-bc41-70c322f508fa",
        "f9f945cc-c166-4f7d-a95f-f0be154c43cf",
        "009b130a-1709-41a6-943d-85eee4889792",
        "a3f765f7-2329-47e0-83eb-0837b4b54b43",
        "fea9e558-206f-444a-8d7f-a3f0301fda8d",
        "9b419098-ccfc-467d-9de0-db18b60d6c28",
        "e6c2174e-3a3f-4193-9782-1bf3b5cfae63",
        "d42c962e-1691-4fa4-8926-c33157423bd2",
        "8d27aa83-a103-4f05-8230-69e857bc3ffd",
        "60cd19b2-6858-4704-b07b-5196e8e24325",
        "31624ea4-1e4f-4f90-ae4f-759a0eb93b61",
        "fcd038f4-6b05-485b-afe3-ce67e05b1695",
        "1207bbe5-2df5-4c86-8f54-1b2675a86859",
        "eea3b0b0-deae-41de-b010-d6d50855d016",
        "ca8b0278-744c-4a3f-a2b8-6ab29d76fa7f",
        "68d37bc8-28b9-49fd-9e02-48a3c9195fdf",
        "8bf13f61-c5cc-4332-aab9-37405d1fdd14",
        "8ceef7de-9408-48d1-8bb9-b8ac3ef73596",
        "7e053a85-b04c-484b-8815-d26ce646c748",
        "dfc09237-85b7-4596-b4e8-0bfbfd1aaeb7",
        "d8d291ab-9dfa-45c0-bfc2-0a81167e3c63",
        "d0834157-d464-4632-b620-147e211e0614",
        "30758f35-fabc-48bc-b410-47450de64c82",
        "7232bc80-a9cb-4668-9449-16b9282a2331",
        "29a194bd-2ecc-44bc-a6a9-6b8a25c3d860",
        "52b43400-117a-4e16-81b8-b510fe987750",
        "52ef0c45-9ba1-4d5e-ba0c-82703196ec6c",
        "9f0fa778-e6ae-4f7b-b4fd-2ccb1bd37eb7",
        "54b57afd-c91c-4d5f-8177-c3fe940bc723",
        "23620661-6eb6-41df-9de4-18ff99e6f35f",
        "c983fe89-6ac3-4395-882e-4b11aa11a99d",
        "d4d01494-e7d0-4a38-aa93-523a77855371",
        "e5a77df6-fd29-48c7-8df6-f625de0179e7",
        "bca45eef-fc64-465f-9106-403814f180a0",
        "3b5c305d-be5e-4209-9ba2-c2d1620a5a4f",
        "14c533a5-c15c-493b-8c7d-7c20a0bc5ea1",
        "7b3b1e40-c75d-4c2c-843b-1599c10123c2",
        "54604482-72aa-4d64-a3bb-9d8dc4a38b41",
        "baf6f609-2dce-4978-840b-b74261c5ba6d",
        "250c536f-6cd9-4707-8706-b682961be032",
        "a9b08140-ae44-409a-9941-22794c3fd097",
        "e516bd18-c46f-46b5-88dc-c7eac5a0f5a9",
        "6a220133-c71f-44df-8912-16f5b72568cb",
        "b63c2adf-b8f3-4e43-8651-44574475621f",
        "01d88287-387b-4a34-b6d3-0931aba8eb1a",
        "eb0cef3d-4e2b-45b3-88df-fc547a763d01",
        "a79dee0f-8579-4e0a-b77f-0a468a3ca71f",
        "62e50edb-03e6-4f95-a6f4-8ff3ef28a32b",
        "337fffe8-cc68-44b7-9636-2433f86ed5a9",
        "bd68f7b7-f8bb-489e-ac29-f8cbfe1978b3",
        "93d2a7d6-06a6-41bf-9632-c24e1f1c917a",
    ]
    rounds = 0
    for i in quiz_list:
        rounds = rounds + 1
        await get(i)
    lol = await get("f183e091-a863-44ec-a1b7-c70eb92e3f6a")
    assert lol is None
    assert await get("8c523af2-6fbf-4940-a5fa-6b6130546892") is None
