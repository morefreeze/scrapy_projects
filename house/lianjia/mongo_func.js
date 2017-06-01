db.system.js.save({
    _id: "convert_lj_community",
    value: function (collection) {
        collection.find().forEach(
            function(doc) {
                positions = doc.position_border.split(';');
                for (i in positions) {
                    positions[i] = positions[i].split(',')
                }
                collection.update({_id: doc._id}, {'$set': {'position_border': positions}});
            }
        )
    }
})

