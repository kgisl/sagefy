Model = require('../../scripts/framework/model')

describe('Model', ->
    it('should create `attributes` on create', ->
        m = new Model()
        expect(m.attributes).to.deep.equal({})
    )

    it('should return url on makeurl if string', ->
        class M extends Model
            url: '/foo'
        m = new M()
        expect(m.makeUrl()).to.equal('/foo')
    )

    it('should call the url function with provided options on makeurl', ->
        class M extends Model
            url: (options) ->
                return '/foo/' + options.id
        m = new M()
        expect(m.makeUrl({id: 23})).to.equal('/foo/23')
    )

    it('should get an attribute', ->
        m = new Model()
        m.attributes.a = 1
        expect(m.get('a')).to.equal(1)
    )

    it('should return undefined if attribute doesn\'t exist', ->
        m = new Model()
        m.attributes.a = 1
        expect(m.get('b')).to.equal(undefined)
    )

    it('should set an key and value', ->
        m = new Model()
        m.set('a', 1)
        expect(m.get('a')).to.equal(1)
    )

    it('should set a full object', ->
        m = new Model()
        m.set({a: 1, b: 2})
        expect(m.get('a')).to.equal(1)
        expect(m.get('b')).to.equal(2)
    )

    it('should set a partial object', ->
        m = new Model()
        m.attributes = {a: 1, b: 2}
        m.set({b: 3, c: 5})
        expect(m.attributes).to.deep.equal({
            a: 1
            b: 3
            c: 5
        })
    )

    it('should trigger change when attributes set', ->
        m = new Model()
        foo = false
        m.on('change', -> foo = true)
        expect(foo).to.be.false
        m.set('a', 1)
        expect(foo).to.be.true
    )

    it('should unset a key', ->
        m = new Model()
        m.attributes = {a: 1, b: 2}
        m.unset('b')
        expect(m.attributes).to.deep.equal({a: 1})
    )

    it('should unset all attributes', ->
        m = new Model()
        m.attributes = {a: 1, b: 2}
        m.unset()
        expect(m.attributes).to.deep.equal({})
    )

    it('should trigger change when attributes unset', ->
        m = new Model()
        m.attributes = {a: 1}
        foo = false
        m.on('change', -> foo = true)
        expect(foo).to.be.false
        m.unset('a')
        expect(foo).to.be.true
    )

    describe('validate', ->
        beforeEach(->
            class @M extends Model
                fields: {
                    name: {
                        type: 'text'
                        validations: {
                            required: true
                        }
                    }
                    email: {
                        type: 'email'
                        validations: {
                            required: true
                            email: true
                        }
                    }
                    password: {
                        type: 'password'
                        validations: {
                            required: true
                            minlength: 8
                        }
                    }
                }
        )

        afterEach(->
            delete @M
        )

        it('should validate a model', ->
            m = new @M()
            m.set({
                name: 'me'
                email: 'a@b.c'
                password: 'abcd1234'
            })
            expect(m.validate()).to.deep.equal([])
        )

        it('should provide validation errors', ->
            m = new @M()
            expect(m.validate()).to.have.length(3)
            m.set('name', 'me')
            expect(m.validate()).to.have.length(2)
            m.set('email', 'a')
            expect(m.validate()).to.have.length(2)
            m.set('email', 'a@b.c')
            expect(m.validate()).to.have.length(1)
            m.set('password', 'abcd')
            expect(m.validate()).to.have.length(1)
            m.set('password', 'abcd1234')
            expect(m.validate()).to.have.length(0)
        )
    )

    describe('restful', ->
        beforeEach(->
            class @M extends Model
                url: (options) ->
                    return '/apples/' + (@get('id') or options.id or  '')
                fields: {
                    name: {
                        type: 'text'
                        validations: {
                            required: true
                        }
                    }
                    email: {
                        type: 'email'
                        validations: {
                            required: true
                            email: true
                        }
                    }
                    password: {
                        type: 'password'
                        validations: {
                            required: true
                            minlength: 8
                        }
                    }
                }
        )

        afterEach(->
            delete @M
        )

        it('should fetch a model from the server', ->
            ajax = sinon.stub(Model::, 'ajax', (options) ->
                options.done({
                    name: 'abcd'
                    email: 'a@b.c'
                    password: 'abcd1234'
                })
            )
            m = new @M()
            m.fetch({id: '23'})
            expect(m.attributes).to.deep.equal({
                name: 'abcd'
                email: 'a@b.c'
                password: 'abcd1234'
            })
            ajax.restore()
        )

        it('should trigger an error on fetching a model', ->
            ajax = sinon.stub(Model::, 'ajax', (options) ->
                options.fail({
                    errors: [
                        {message: 'Uh oh.'}
                    ]
                })
            )
            m = new @M()
            spy = sinon.spy()
            m.on('error', spy)
            m.fetch({id: '23'})
            expect(spy).to.be.called
            ajax.restore()
        )

        it('should call parse after fetching a model', ->
            ajax = sinon.stub(Model::, 'ajax', (options) ->
                options.done({
                    name: 'abcd'
                    email: 'a@b.c'
                    password: 'abcd1234'
                })
            )
            spy = sinon.spy(Model::, 'parse')
            m = new @M()
            m.fetch({id: '23'})
            expect(spy).to.be.called
            ajax.restore()
            spy.restore()
        )

        it('should validate a model before save', ->
            spy = sinon.spy(Model::, 'validate')
            ajax = sinon.stub(Model::, 'ajax')
            m = new @M()
            m.save()
            expect(spy).to.be.called
            ajax.restore()
            spy.restore()
        )

        it('should return validation errors on save if problem', ->
            ajax = sinon.stub(Model::, 'ajax')
            m = new @M()
            m.save()
            expect(m.save()).to.have.length(3)
            ajax.restore()
        )

        it('should save a model', ->
            ajax = sinon.stub(Model::, 'ajax', (options) ->
                options.done({
                    id: '23'
                    name: 'abcd'
                    email: 'a@b.c'
                    password: 'abcd1234'
                })
            )
            m = new @M()
            m.set({
                name: 'abcd'
                email: 'a@b.c'
                password: 'abcd1234'
            })
            m.save()
            expect(m.get('id')).to.equal('23')
            ajax.restore()
        )

        it('should parse after saving a model', ->
            ajax = sinon.stub(Model::, 'ajax', (options) ->
                options.done({
                    id: '23'
                    name: 'abcd'
                    email: 'a@b.c'
                    password: 'abcd1234'
                })
            )
            spy = sinon.spy(Model::, 'parse')
            m = new @M()
            m.set({
                name: 'abcd'
                email: 'a@b.c'
                password: 'abcd1234'
            })
            m.save()
            expect(spy).to.be.called
            spy.restore()
            ajax.restore()
        )

        it('should throw an error on save', ->
            ajax = sinon.stub(Model::, 'ajax', (options) ->
                options.fail({
                    errors: [
                        {message: 'Uh oh.'}
                    ]
                })
            )
            m = new @M()
            spy = sinon.spy()
            m.on('error', spy)
            m.set({
                name: 'abcd'
                email: 'a@b.c'
                password: 'abcd1234'
            })
            m.save()
            expect(spy).to.be.called
            ajax.restore()
        )
    )

    describe('#ajax', ->
        it.skip('should make a GET request with no data', ->

        )

        it.skip('should make a POST request with data', ->

        )

        it.skip('should make a DELETE request', ->

        )
    )
)
