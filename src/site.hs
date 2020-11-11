--------------------------------------------------------------------------------
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
import           Data.Monoid (mappend)
import           Hakyll
import           Text.Pandoc.Options
import           Hakyll.Core.UnixFilter (unixFilter)
import qualified Crypto.Hash as CH
import           Data.ByteString.UTF8 as B
import           System.Environment (lookupEnv)
import qualified Data.List as DL
import qualified Data.Vector as Vector
import qualified Data.Aeson as Aeson
import qualified Data.HashMap.Strict as HashMap
import qualified Data.Text as T
import Hakyll.Core.Compiler

pandocMathCompiler =
    let defaultExtensions = writerExtensions defaultHakyllWriterOptions
        writerOptions = defaultHakyllWriterOptions {
                          writerHTMLMathMethod = MathJax ""
                        }
    in pandocCompilerWith defaultHakyllReaderOptions writerOptions
    
--------------------------------------------------------------------------------
main :: IO ()
main = do
  sassLoadPath <- lookupEnv "SASSLOADPATH"
  let sassCompiler = withItemBody (unixFilter "sass" (["-s", "--scss"]
                                                      ++ additionalOptions))
                     where
                       additionalOptions = case sassLoadPath of
                         Nothing -> []
                         Just path -> ["-I", path]
  hakyll $ do
    -- All global images are just copied as it
    match "images/**" $ do
        route   idRoute
        compile copyFileCompiler

    -- All html files at the root folder should be kept intact
    match "*.html" $ do
      route idRoute
      compile $ do
      getResourceBody
        >>= applyAsTemplate customDefaultContext
        >>= loadAndApplyTemplate "templates/default.html" customDefaultContext
        >>= relativizeUrls

    -- Copy and compress the CSS
    match "css/*.css" $ do
        route   idRoute
        compile compressCssCompiler

    -- Copy and compile the SCSS style file
    match "css/default.scss" $ do
        route   $ setExtension "css"
        compile $ getResourceString >>=
            sassCompiler >>=
            return . fmap compressCss

    -- All markdown/org-mode files are converted using pandoc
    match (fromGlob "*.org" .||. fromGlob "*.md") $ do
        route   $ setExtension "html"
        compile $ pandocMathCompiler
            >>= loadAndApplyTemplate "templates/default.html" customDefaultContext
            >>= relativizeUrls

    match "posts/*" $ do
        route $ setExtension "html"
        compile $ pandocCompiler
            >>= loadAndApplyTemplate "templates/post.html"    postCtx
            >>= loadAndApplyTemplate "templates/default.html" postCtx
            >>= relativizeUrls

    create ["archive.html"] $ do
        route idRoute
        compile $ do
            posts <- recentFirst =<< loadAll "posts/*"
            let archiveCtx =
                    listField "posts" postCtx (return posts) `mappend`
                    constField "title" "Archives"            `mappend`
                    customDefaultContext

            makeItem ""
                >>= loadAndApplyTemplate "templates/archive.html" archiveCtx
                >>= loadAndApplyTemplate "templates/default.html" archiveCtx
                >>= relativizeUrls

    match "blog.html" $ do
        route idRoute
        compile $ do
            posts <- recentFirst =<< loadAll "posts/*"
            let indexCtx =
                    listField "posts" postCtx (return posts) `mappend`
                    constField "title" "Home"                `mappend`
                    customDefaultContext

            getResourceBody
                >>= applyAsTemplate indexCtx
                >>= loadAndApplyTemplate "templates/default.html" indexCtx
                >>= relativizeUrls

    match "templates/*" $ compile templateBodyCompiler

    match "templates/partials/*" $ compile templateBodyCompiler

    match "menu.json" $ do
      compile getResourceBody

hashFromString :: String -> String
hashFromString str =
  show (CH.hash (B.fromString str) :: CH.Digest CH.SHA512)

cssHashContext :: Context String
cssHashContext = field "cssHash" $ \_ -> do
  -- Takes the compiled style.css file...
  styleBody <- loadBody "css/default.scss" :: Compiler String
  -- Compute a hash on it
  return $ hashFromString styleBody


-- Use: $partialWithContext("template.html", "key1", "value1", "key2", "value2")$
partialWithContext :: Context String
partialWithContext = functionField "partialWithContext" $ \args page -> do
  case args of
    [] -> fail "partialWithContext: ERROR: You need to specify a file.\nUsage: $partialWithContext(\"template.html\", \"key1\", \"value1\", \"key2\", \"value2\", ...)$"
    path : key_values -> do
      -- Load the template
      template <- loadBody (fromFilePath path)
      -- TODO: Possible to add the current context?
      -- Convert key_values (looks like ["key1", "val1", "key2", "val2"]) into a context
      context :: Context String <- fromMaybeOrFail "partialWithContext: ERROR: you need to have an even number of arguments (key/value)." $ listOfStringToContext key_values
      -- Apply the template
      itemBody <$> applyTemplate template (context <> partialWithContext) page

fromMaybeOrFail :: MonadFail m => String -> Maybe a -> m a
fromMaybeOrFail x maybe_a = maybe (fail x) pure maybe_a

-- Great post: https://hashanp.xyz/posts/hakyll.html
-- Use: $partialWithContextJSONFile("template.html", "menu.json")$
-- or if you want to forward some stuff from the current context:
-- $partialWithContextJSONFile("template.html", "menu.json", "currentSection", currentSection)$
-- where "menu.json" contains something like:
--- {
---     "date": "10/11/2020",
---     "urls": [
---         {
---             "name": "Home",
---             "link": "/"
---         },
---         {
---             "name": "Contact",
---             "link": "/contact"
---         }
---     ]
--- }
--- And "template.html" contains something like:
--- <ul>
---   The date is $date$.<br/>
---   $for(urls)$
---   <li><a href="$link$">$name$</a></li>
---   $endfor$
--- </ul>
partialWithContextJSONFile :: Context String
partialWithContextJSONFile = functionField "partialWithContextJSONFile" $ \args page -> do
  case args of
    (pathTemplate:pathJson:remainingArguments) -> do
      -- Load the template
      template <- loadBody (fromFilePath pathTemplate)
      -- TODO: Possible to add the current context?
      -- ### For now you need to put something like:
      -- match "menu.json" $ do
      --  compile getResourceBody
      -- ### in your compile rules.
      -- NB: this line is not enough:
      jsonBody <- B.fromString <$> loadBody (fromFilePath pathJson)
      remainingContext :: Context String <- fromMaybeOrFail "partialWithContextJSONFile: ERROR: you need to have an even number of arguments (key/value)." $ listOfStringToContext remainingArguments
      let eitherJson = Aeson.eitherDecodeStrict' jsonBody
      case eitherJson of
        Left err -> fail $ "partialWithContextJSONFile: ERROR " ++ err
        Right (json :: Aeson.Value) ->
          let jsonContext :: Context String = contextFromJson json in
            -- Apply the template
            itemBody <$> applyTemplate template (remainingContext <> jsonContext <> partialWithContext) page
    _ -> fail $ "partialWithContextJSONFile: ERROR: You need to specify a file.\n" ++
                "Usage: $partialWithContextJSONFile(\"template.html\", \"yourfile.json\")$"

contextFromJson :: Aeson.Value -> Context String
contextFromJson (Aeson.Object o) =
  HashMap.foldrWithKey
    (\key_txt value oldContext -> do
       let key = T.unpack key_txt
       -- Check if the key is associated with a string/number/object value in the
       -- json file
       case value of
         Aeson.Bool b -> (boolField key $ \_ -> b) <> oldContext
         Aeson.String text -> (constField key $ T.unpack text)
           <> oldContext
         Aeson.Number n -> (constField key $ show n)
           <> oldContext
         Aeson.Null -> (constField key "")
           <> oldContext
         Aeson.Object o' ->
           -- If it's an object, we try to define a notation abc.def
           let contextO' = contextFromJson (Aeson.Object o') in
             (Context $ \k args item -> do
                 case DL.stripPrefix (key ++ ".") k of
                   Nothing -> noResult $ "No result in form " ++ key ++ "."
                   Just k' -> ((unContext contextO') k' args item)) <> oldContext
         Aeson.Array v ->
            -- It's a vector of values: it means that we want to create a list!
            -- Something like "abc": [{"name": "Alice"}, {"name": "Bob"}]
            (Context $ \k args item -> do
                if k == key then
                  return $ ListField (contextInsideLoop item) (Vector.toList (Vector.map (\x -> Item "" x) v))
                else
                  noResult $ "No result in form " ++ key) <> oldContext
          where
            contextInsideLoop :: Item String -> Context Aeson.Value
            contextInsideLoop oldItem = Context f
              where
                f (key :: String) args (item :: Item Aeson.Value) =
                  let contextItem = contextFromJson (itemBody item) in
                    -- Note sure item is really meaningfull here...
                    (unContext contextItem) key args oldItem
    )
    (mempty :: Context String)
    o
contextFromJson _ = mempty

listOfStringToContext :: [String] -> Maybe (Context String)
listOfStringToContext [] = Just mempty
listOfStringToContext [k] = Nothing
listOfStringToContext (k:val:r) = do
  context <- (listOfStringToContext r)
  let currentField = constField k val
  return (currentField <> context)

includeContainerContext :: Context String
includeContainerContext = Context $ \key args item -> do
  if key == "includeContainerBool" then do
    meta <- getMetadataField (itemIdentifier item) "includeContainer"
    case meta of
      Just "false" -> fail "IncludeContainer has been disabled"
      Just m -> return $ StringField m
      Nothing -> return $ StringField "True"
  else
    noResult ""


customDefaultContext :: Context String
customDefaultContext =
  -- Order of <> matters
  partialWithContextJSONFile
  <> partialWithContext
  <> includeContainerContext
  <> cssHashContext
  <> defaultContext


--------------------------------------------------------------------------------
postCtx :: Context String
postCtx =
    dateField "date" "%B %e, %Y" `mappend`
    customDefaultContext
