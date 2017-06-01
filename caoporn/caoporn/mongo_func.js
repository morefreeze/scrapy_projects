db.system.js.save({
    _id: "convert",
    value: function () {
        db.video.find({'$or': [{'length': {'$type': 2}}, {'views': {'$type': 2}}]}).forEach(
            function(doc){
                length=0;
                sp=doc.length.split(':');
                for (i in sp){
                    length=length*60+parseInt(sp[i]);
                }
                db.video.update({'_id': doc._id},
                    {'$set': {'views': parseInt(doc.views), 'length': length}}
                );
            }
        );
    }
})

