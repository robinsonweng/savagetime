# This branch is for restful version of the website

# api doc

- video url expire
    - request head add date to md5 with salt
    - should work with nginx

## 影片清單
```
api/video/v1/list?num=AMOUNT&series=ID&episode=EPISODE
```
### parameter value:
- AMOUNT
- EPISODE

### response:


### 考量: 
- 最大回傳數量預設值與上限
- 標題, 集數, 季度, 年月
- 如果沒有 `episode` 參數, 改為回傳整個系列

<hr></hr>

## 上傳檔案

```
api/video/v1/upload?resumable=BOOLEAN&part=snippet, status, detail
```

### parameter value:

### response

### 考量
- 順序
    1. 上傳metadata
    2. server端驗證metadata
    3. 回傳upload id
    4. client 一段一段上傳
    5. md5驗證檔案是否損毀
- 如何驗證檔案?
    - md5?
- 驗證檔案大小(Never trust user input)
- 如何設計upload id?


<hr></hr>

## 搜尋

```
api/search/v1/list?num=AMOUNT&keyword=KEYWORD
```

### parameter value
### response
### 考量

## authorize

```
api/auth/v1/user?username=USERNAME&password=PASSWORD
```

### parameter value
### response
### 考量
- 加密
    - 加密的神奇之處就在於我在資料庫只有加鹽檔案，但我卻可以透過已經加鹽的資料來判斷帳密是否正確
    - session
        - auth head
