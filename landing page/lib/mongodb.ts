import { MongoClient, type Db } from 'mongodb'

const uri = process.env.MONGODB_URI!
const options = {}

// Singleton pattern — reuse connection across hot-reloads in dev
declare global {
  // eslint-disable-next-line no-var
  var _mongoClientPromise: Promise<MongoClient> | undefined
}

if (!uri) {
  throw new Error('MONGODB_URI is not set in .env.local')
}

let clientPromise: Promise<MongoClient>

if (process.env.NODE_ENV === 'development') {
  if (!global._mongoClientPromise) {
    const client = new MongoClient(uri, options)
    global._mongoClientPromise = client.connect()
  }
  clientPromise = global._mongoClientPromise
} else {
  const client = new MongoClient(uri, options)
  clientPromise = client.connect()
}

export default clientPromise

export async function getDb(): Promise<Db> {
  const client = await clientPromise
  return client.db()
}
